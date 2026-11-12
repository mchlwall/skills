# Templates

## Contents
- settings.gradle
- build.gradle
- config/TestConfig.java, config/Endpoints.java
- utils/ApiClient.java
- utils/ResponseLoggingExtension.java
- utils/TestTimeouts.java, utils/JsonUtils.java
- builders/TaskRequest.java
- Example test class
- resources/logback.xml, quarantined-tests.json

## settings.gradle

```groovy
rootProject.name = 'project-tracker-api-tests'
```

## build.gradle

```groovy
import groovy.json.JsonBuilder
import groovy.json.JsonSlurper
import groovy.xml.XmlSlurper

plugins {
    id 'java'
    id 'com.diffplug.spotless' version '8.6.0'
}

repositories {
    mavenCentral()
}

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(17)
    }
}

dependencies {
    testImplementation platform('org.junit:junit-bom:6.1.0')
    testImplementation 'org.junit.jupiter:junit-jupiter'
    testImplementation 'org.junit-pioneer:junit-pioneer:2.3.0'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'

    testImplementation 'io.rest-assured:rest-assured:6.0.0'
    testImplementation 'org.hamcrest:hamcrest:3.0'
    testImplementation 'ch.qos.logback:logback-classic:1.5.34'

    testImplementation platform('com.fasterxml.jackson:jackson-bom:2.21.4')
    testImplementation 'com.fasterxml.jackson.core:jackson-databind'

    testCompileOnly 'org.projectlombok:lombok:1.18.46'
    testAnnotationProcessor 'org.projectlombok:lombok:1.18.46'
}

spotless {
    java {
        target 'src/**/*.java'
        googleJavaFormat()
    }
}

def quarantineFile = file('quarantined-tests.json')

tasks.withType(Test).configureEach {
    testClassesDirs = sourceSets.test.output.classesDirs
    classpath = sourceSets.test.runtimeClasspath
    systemProperty 'baseUrl', System.getenv('BASE_URL') ?: 'http://localhost:8080'
    testLogging {
        events 'PASSED', 'FAILED', 'SKIPPED'
        showStandardStreams = true
    }
    outputs.upToDateWhen { false }
    outputs.cacheIf { false }
    if (quarantineFile.exists()) {
        filter {
            new JsonSlurper().parse(quarantineFile).each { pattern ->
                println "Excluding quarantined test: ${pattern}"
                excludeTestsMatching pattern.toString()
            }
        }
    }
    finalizedBy 'testReportUI', 'generateTestRunSummary'
}

test {
    useJUnitPlatform {
        excludeTags 'unit'
    }
}

def suites = [
    testSmoke   : 'smoke',
    testProjects: 'projects',
    testTasks   : 'tasks',
    testUnit    : 'unit',
]

suites.each { taskName, tag ->
    tasks.register(taskName, Test) {
        description = "Run tests tagged @Tag(\"${tag}\")"
        group = 'verification'
        useJUnitPlatform {
            includeTags tag
        }
    }
}

tasks.register('verifyTestTags') {
    description = 'Fail if any test class is missing a @Tag annotation'
    group = 'verification'
    def testFiles = sourceSets.test.allJava
    inputs.files(testFiles)
    doLast {
        def testAnnotation = /@(Test|ParameterizedTest|RepeatedTest|RetryingTest)\b/
        def tagAnnotation = /@Tag\s*\(/
        def missing = testFiles.files.findAll { f ->
            def content = f.text
            content =~ testAnnotation && !(content =~ tagAnnotation)
        }.collect { it.path - (projectDir.path + '/') }
        if (missing) {
            throw new GradleException(
                "Test classes must have a @Tag annotation. Missing in:\n  " + missing.join("\n  ") +
                "\n\nSee docs/suites-and-ci.md for available tags.")
        }
    }
}
check.dependsOn verifyTestTags

tasks.register('testReportUI') {
    description = 'Brand the Gradle HTML test reports'
    def reportsRoot = layout.buildDirectory.dir('reports/tests').get().asFile
    def runbookUrl = 'https://github.com/<you>/project-tracker-api-tests/blob/main/docs/triage-runbook.md'
    doLast {
        if (!reportsRoot.exists()) return
        reportsRoot.eachDir { dir ->
            def index = new File(dir, 'index.html')
            if (!index.exists() || index.text.contains('data-report-ui-injected')) return
            def banner = """<div class="custom-banner" data-report-ui-injected="true">📋 Project Tracker API Test Report</div>"""
            def support = """<div class="support-box"><strong>Investigating failures?</strong> <a href="${runbookUrl}" target="_blank">Triage runbook</a></div>"""
            def styles = """<style>
                .custom-banner { background:#3b2f80; color:#ece9ff; padding:1em; margin-bottom:2em; font-size:1.4em; text-align:center; }
                .support-box { margin-top:20px; padding:10px; background:#f1effc; border-left:4px solid #3b2f80; }
            </style>"""
            index.text = index.text
                .replace('<body>', "<body>\n${banner}")
                .replace('</head>', "${styles}\n</head>")
                .replaceFirst(/<div id="content">/, "<div id=\"content\">${support}")
            println "Updated report UI: ${index}"
        }
    }
}

tasks.register('generateTestRunSummary') {
    description = 'Write build/artifacts/testRunSummary.json from JUnit XML results'
    def resultsRoot = layout.buildDirectory.dir('test-results').get().asFile
    def outputFile = layout.buildDirectory.file('artifacts/testRunSummary.json').get().asFile
    doLast {
        def totals = [tests: 0, failures: 0, errors: 0, skipped: 0]
        def failedTests = []
        if (resultsRoot.exists()) {
            resultsRoot.eachFileRecurse(groovy.io.FileType.FILES) { f ->
                if (!(f.name ==~ /TEST-.*\.xml/)) return
                def suite = new XmlSlurper().parse(f)
                totals.keySet().each { k -> totals[k] += (suite."@${k}".toString() ?: '0') as Integer }
                suite.testcase.findAll { it.failure.size() > 0 || it.error.size() > 0 }.each { tc ->
                    def node = tc.failure.size() > 0 ? tc.failure[0] : tc.error[0]
                    def specPath = tc.@classname.toString()
                    failedTests << [
                        suite      : f.parentFile.name,
                        specPath   : specPath,
                        testName   : tc.@name.toString(),
                        error      : node.@message.toString() ?: node.text().take(2000),
                        rerun      : "./gradlew test --tests \"${specPath}\"",
                    ]
                }
            }
        }
        def summary = [
            suiteType  : System.getenv('SUITE_TYPE') ?: 'local',
            runId      : System.getenv('GITHUB_RUN_ID') ?: 'local',
            repo       : System.getenv('GITHUB_REPOSITORY') ?: rootProject.name,
            commit     : System.getenv('GITHUB_SHA') ?: '',
            isScheduled: System.getenv('GITHUB_EVENT_NAME') == 'schedule',
            baseUrl    : System.getenv('BASE_URL') ?: 'http://localhost:8080',
            totals     : totals,
            failedTests: failedTests,
        ]
        outputFile.parentFile.mkdirs()
        outputFile.text = new JsonBuilder(summary).toPrettyString()
        println "Generated test run summary: ${outputFile} (failed: ${failedTests.size()})"
    }
}
```

Notes:
- Gradle 9 requires `testClassesDirs` / `classpath` on custom `Test` tasks, hence the `configureEach`.
- With `@RetryingTest`, earlier failed attempts appear as `<skipped>`, so a `<failure>` means every attempt failed.

## config/TestConfig.java

```java
package config;

public final class TestConfig {
  private TestConfig() {}

  public static String baseUrl() {
    String fromProperty = System.getProperty("baseUrl");
    if (fromProperty != null && !fromProperty.isBlank()) {
      return fromProperty;
    }
    String fromEnv = System.getenv("BASE_URL");
    return fromEnv != null && !fromEnv.isBlank() ? fromEnv : "http://localhost:8080";
  }
}
```

## config/Endpoints.java

```java
package config;

public final class Endpoints {
  private Endpoints() {}

  public static final String HEALTH = "/health";
  public static final String PROJECTS = "/api/projects";
  public static final String PROJECT_BY_ID = "/api/projects/{id}";
  public static final String PROJECT_TASKS = "/api/projects/{id}/tasks";
  public static final String TASK_BY_ID = "/api/tasks/{id}";
}
```

## utils/ApiClient.java

Argument order is always `(endpoint, body?, pathParams...)`.

```java
package utils;

import config.TestConfig;
import io.restassured.RestAssured;
import io.restassured.http.ContentType;
import io.restassured.response.Response;
import io.restassured.specification.RequestSpecification;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ApiClient {
  private static final Logger log = LoggerFactory.getLogger(ApiClient.class);

  private final String baseUrl;

  public ApiClient() {
    this(TestConfig.baseUrl());
  }

  public ApiClient(String baseUrl) {
    this.baseUrl = baseUrl;
  }

  private RequestSpecification request() {
    return RestAssured.given().baseUri(baseUrl).accept(ContentType.JSON);
  }

  public Response get(String endpoint, Object... pathParams) {
    log.info("🔍 GET {}{}", baseUrl, endpoint);
    Response response = request().when().get(endpoint, pathParams).then().extract().response();
    ResponseLoggingExtension.setResponse(response, null);
    return response;
  }

  public Response getWithQueryParams(
      String endpoint, Map<String, ?> queryParams, Object... pathParams) {
    log.info("🔍 GET {}{} {}", baseUrl, endpoint, queryParams);
    Response response =
        request()
            .queryParams(queryParams)
            .when()
            .get(endpoint, pathParams)
            .then()
            .extract()
            .response();
    ResponseLoggingExtension.setResponse(response, queryParams);
    return response;
  }

  public Response post(String endpoint, Object body, Object... pathParams) {
    log.info("🔍 POST {}{}", baseUrl, endpoint);
    Response response =
        request()
            .contentType(ContentType.JSON)
            .body(body)
            .when()
            .post(endpoint, pathParams)
            .then()
            .extract()
            .response();
    ResponseLoggingExtension.setResponse(response, body);
    return response;
  }

  public Response put(String endpoint, Object body, Object... pathParams) {
    log.info("🔍 PUT {}{}", baseUrl, endpoint);
    Response response =
        request()
            .contentType(ContentType.JSON)
            .body(body)
            .when()
            .put(endpoint, pathParams)
            .then()
            .extract()
            .response();
    ResponseLoggingExtension.setResponse(response, body);
    return response;
  }

  public Response patch(String endpoint, Object body, Object... pathParams) {
    log.info("🔍 PATCH {}{}", baseUrl, endpoint);
    Response response =
        request()
            .contentType(ContentType.JSON)
            .body(body)
            .when()
            .patch(endpoint, pathParams)
            .then()
            .extract()
            .response();
    ResponseLoggingExtension.setResponse(response, body);
    return response;
  }

  public Response delete(String endpoint, Object... pathParams) {
    log.info("🔍 DELETE {}{}", baseUrl, endpoint);
    Response response = request().when().delete(endpoint, pathParams).then().extract().response();
    ResponseLoggingExtension.setResponse(response, null);
    return response;
  }
}
```

Add methods here (headers, form data, raw string bodies) rather than calling RestAssured from a test.

## utils/ResponseLoggingExtension.java

Logs request/response only when a test fails, keeping passing output quiet.

```java
package utils;

import io.restassured.response.Response;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.api.extension.TestWatcher;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ResponseLoggingExtension implements TestWatcher {
  private static final Logger log = LoggerFactory.getLogger(ResponseLoggingExtension.class);
  private static final ThreadLocal<Response> latestResponse = new ThreadLocal<>();
  private static final ThreadLocal<Object> latestRequestBody = new ThreadLocal<>();

  public static void setResponse(Response response, Object requestBody) {
    latestResponse.set(response);
    latestRequestBody.set(requestBody);
  }

  @Override
  public void testFailed(ExtensionContext context, Throwable cause) {
    Response response = latestResponse.get();
    if (response != null) {
      log.info("❌ Test failed: {}", context.getDisplayName());
      log.info("Status: {}", response.getStatusCode());
      log.info("Request Body: {}", latestRequestBody.get());
      log.info("Response Body: {}", response.getBody().prettyPrint());
    }
    clear();
  }

  @Override
  public void testSuccessful(ExtensionContext context) {
    log.info("✅ Test passed: {}", context.getDisplayName());
    clear();
  }

  private static void clear() {
    latestResponse.remove();
    latestRequestBody.remove();
  }
}
```

## utils/TestTimeouts.java

```java
package utils;

public final class TestTimeouts {
  private TestTimeouts() {}

  public static final long S = 5;
  public static final long M = 15;
  public static final long L = 30;
}
```

## utils/JsonUtils.java

Fixtures live in `src/test/resources/fixtures/` and are read from the classpath.

```java
package utils;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.Map;

public final class JsonUtils {
  public static final String MALFORMED_JSON = "{this is not valid json";
  private static final ObjectMapper MAPPER = new ObjectMapper();

  private JsonUtils() {}

  public static String readFixture(String fileName) {
    try (InputStream in = JsonUtils.class.getResourceAsStream("/fixtures/" + fileName)) {
      if (in == null) {
        throw new IllegalArgumentException("Fixture not found: fixtures/" + fileName);
      }
      return new String(in.readAllBytes(), StandardCharsets.UTF_8);
    } catch (IOException e) {
      throw new RuntimeException("Failed to read fixture: " + fileName, e);
    }
  }

  public static Map<String, Object> loadSubstituteJson(String fileName, Map<String, String> values) {
    String raw = readFixture(fileName);
    for (Map.Entry<String, String> entry : values.entrySet()) {
      raw = raw.replace("@" + entry.getKey() + "@", entry.getValue());
    }
    try {
      return MAPPER.readValue(raw, new TypeReference<>() {});
    } catch (IOException e) {
      throw new RuntimeException("Fixture is not valid JSON after substitution: " + fileName, e);
    }
  }
}
```

Example fixture `fixtures/create-project.json`:

```json
{
  "name": "@name@",
  "description": "Created by API tests"
}
```

## builders/TaskRequest.java

`NON_NULL` keeps unset fields out of the body, so tests can check server-side defaults (e.g. `status`).

```java
package builders;

import com.fasterxml.jackson.annotation.JsonInclude;
import java.time.LocalDate;
import java.util.UUID;
import lombok.Builder;
import lombok.Value;

@Value
@Builder(toBuilder = true)
@JsonInclude(JsonInclude.Include.NON_NULL)
public class TaskRequest {
  String title;
  String description;
  String status;
  String priority;
  String dueDate;

  public static TaskRequest validTask() {
    return TaskRequest.builder()
        .title("API test task " + UUID.randomUUID())
        .description("Created by API tests")
        .priority("MEDIUM")
        .dueDate(LocalDate.now().plusDays(7).toString())
        .build();
  }
}
```

Derive variants with `validTask().toBuilder().title("").build()`.
Unit tests for builders go in `src/test/java/builders/` with `@Tag("unit")`.

## Example test class

`src/test/java/apiTests/tasks/TasksTests.java`. IDs are read with `jsonPath().getString(...)` so it works
whether the API uses numeric or string IDs.

```java
package apiTests.tasks;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;

import builders.TaskRequest;
import config.Endpoints;
import io.restassured.response.Response;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.junit.jupiter.api.extension.ExtendWith;
import utils.ApiClient;
import utils.JsonUtils;
import utils.ResponseLoggingExtension;
import utils.TestTimeouts;

@Tag("tasks")
@ExtendWith(ResponseLoggingExtension.class)
class TasksTests {
  private static final ApiClient apiClient = new ApiClient();

  private static String createProject() {
    Map<String, Object> body =
        JsonUtils.loadSubstituteJson(
            "create-project.json", Map.of("name", "API test project " + UUID.randomUUID()));
    Response response = apiClient.post(Endpoints.PROJECTS, body);
    assertThat(response.statusCode(), is(201));
    return response.jsonPath().getString("id");
  }

  private static String createTask(String projectId) {
    Response response = apiClient.post(Endpoints.PROJECT_TASKS, TaskRequest.validTask(), projectId);
    assertThat(response.statusCode(), is(201));
    return response.jsonPath().getString("id");
  }

  @Test
  @Timeout(value = TestTimeouts.M, unit = TimeUnit.SECONDS)
  @DisplayName("POST /api/projects/{id}/tasks creates a task that defaults to TODO")
  void createTaskDefaultsToTodo() {
    String projectId = createProject();
    TaskRequest task = TaskRequest.validTask();

    Response response = apiClient.post(Endpoints.PROJECT_TASKS, task, projectId);

    assertThat(response.statusCode(), is(201));
    assertThat(response.jsonPath().getString("id"), not(emptyOrNullString()));
    assertThat(response.jsonPath().getString("projectId"), is(projectId));
    assertThat(response.path("title"), is(task.getTitle()));
    assertThat(response.path("status"), is("TODO"));
    assertThat(response.path("priority"), oneOf("LOW", "MEDIUM", "HIGH"));
    assertThat(response.path("dueDate"), is(task.getDueDate()));
    assertThat(response.path("createdAt"), matchesPattern("^\\d{4}-\\d{2}-\\d{2}T.+"));
  }

  @Test
  @Timeout(value = TestTimeouts.M, unit = TimeUnit.SECONDS)
  @DisplayName("POST /api/projects/{id}/tasks rejects a blank title with 400")
  void blankTitleRejected() {
    TaskRequest invalid = TaskRequest.validTask().toBuilder().title("").build();

    Response response = apiClient.post(Endpoints.PROJECT_TASKS, invalid, createProject());

    assertThat(response.statusCode(), is(400));
    assertThat(response.path("error"), not(emptyOrNullString()));
  }

  @Test
  @Timeout(value = TestTimeouts.S, unit = TimeUnit.SECONDS)
  @DisplayName("GET /api/tasks/{id} returns 404 for an unknown id")
  void getUnknownTaskReturns404() {
    Response response = apiClient.get(Endpoints.TASK_BY_ID, "does-not-exist");

    assertThat(response.statusCode(), is(404));
  }

  @Test
  @Timeout(value = TestTimeouts.L, unit = TimeUnit.SECONDS)
  @DisplayName("PATCH /api/tasks/{id} moves a task to DONE without changing createdAt")
  void completeTask() {
    String taskId = createTask(createProject());
    Response before = apiClient.get(Endpoints.TASK_BY_ID, taskId);

    Response patched = apiClient.patch(Endpoints.TASK_BY_ID, Map.of("status", "DONE"), taskId);

    assertThat(patched.statusCode(), is(200));
    assertThat(patched.path("status"), is("DONE"));
    assertThat(patched.path("createdAt"), is(before.<String>path("createdAt")));
  }

  @Test
  @Timeout(value = TestTimeouts.M, unit = TimeUnit.SECONDS)
  @DisplayName("PATCH /api/tasks/{id} rejects an unknown status with 400")
  void unknownStatusRejected() {
    String taskId = createTask(createProject());

    Response response =
        apiClient.patch(Endpoints.TASK_BY_ID, Map.of("status", "SOMEDAY"), taskId);

    assertThat(response.statusCode(), is(400));
  }

  @Test
  @Timeout(value = TestTimeouts.L, unit = TimeUnit.SECONDS)
  @DisplayName("GET /api/projects/{id}/tasks?status=DONE returns only done tasks")
  void filterTasksByStatus() {
    String projectId = createProject();
    createTask(projectId);
    String doneTaskId = createTask(projectId);
    apiClient.patch(Endpoints.TASK_BY_ID, Map.of("status", "DONE"), doneTaskId);

    Response response =
        apiClient.getWithQueryParams(Endpoints.PROJECT_TASKS, Map.of("status", "DONE"), projectId);

    assertThat(response.statusCode(), is(200));
    assertThat(response.jsonPath().getList("id", String.class), contains(doneTaskId));
    assertThat(response.jsonPath().getList("status", String.class), everyItem(is("DONE")));
  }

  @Test
  @Timeout(value = TestTimeouts.L, unit = TimeUnit.SECONDS)
  @DisplayName("DELETE /api/projects/{id} removes the project and its tasks")
  void deleteProjectRemovesTasks() {
    String projectId = createProject();
    String taskId = createTask(projectId);

    Response deleted = apiClient.delete(Endpoints.PROJECT_BY_ID, projectId);

    assertThat(deleted.statusCode(), is(204));
    assertThat(apiClient.get(Endpoints.PROJECT_BY_ID, projectId).statusCode(), is(404));
    assertThat(apiClient.get(Endpoints.TASK_BY_ID, taskId).statusCode(), is(404));
  }
}
```

Adjust paths, status codes, field names and cascade behaviour to whatever the app actually does.
A `ProjectsTests` class (`@Tag("projects")`) follows the same shape: create, list, get, rename via PATCH,
duplicate-name and blank-name validation, delete.

## src/test/resources/logback.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <appender name="Console" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{HH:mm:ss} %-5level %msg%n</pattern>
        </encoder>
    </appender>
    <logger name="org.apache.http" level="WARN"/>
    <root level="INFO">
        <appender-ref ref="Console"/>
    </root>
</configuration>
```

## quarantined-tests.json

Optional. A JSON array of Gradle test filter patterns excluded from every `Test` task:

```json
["apiTests.projects.ProjectArchiveTests"]
```
