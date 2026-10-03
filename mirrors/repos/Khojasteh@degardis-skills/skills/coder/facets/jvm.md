---
title: JVM build and platform
category: Runtime and platform
x-claim-provenance:
- claim: Maven dependency mediation uses the version of the dependency nearest to the project in the dependency tree, the first declaration wins when two versions are at the same depth, and dependency management takes precedence over mediation for transitive dependencies.
  source: https://maven.apache.org/guides/introduction/introduction-to-dependency-mechanism.html
- claim: Gradle considers all requested versions across the dependency graph and by default selects the highest version.
  source: https://docs.gradle.org/current/userguide/graph_resolution.html
- claim: By default Gradle uses the same Java toolchain for running Gradle and for building JVM projects, and a declared Java toolchain selects the JDK used to compile, test, and run independently of the JVM running Gradle.
  source: https://docs.gradle.org/current/userguide/toolchains.html
---

The configured JDK toolchain, source and release targets, Maven or Gradle versions and wrappers, repositories, lock or verification policy, dependency constraints, imported platforms or BOMs, plugins, modules, and deployment runtime define the JVM build environment, and JDK, build-tool, plugin, module, and runtime features exist only where the project's configured versions support them. Without a declared toolchain, Gradle compiles and tests with whichever JVM runs Gradle itself, so the same build can produce different results on different machines.

Each resolved dependency has an owning declaration, and dependencies and toolchains change through those declarations. The two build tools resolve version conflicts in opposite directions. Maven takes the version nearest the project in the dependency tree, or the first declaration at equal depth, unless `dependencyManagement` pins it, so adding a direct dependency can downgrade a transitive one; Gradle selects the highest version requested anywhere in the graph. Observable state is therefore the effective build and its resolved compile, runtime, and test graphs rather than build-file text alone, including conflict mediation, variants, capabilities, exclusions, classifiers, plugin classpaths, and generated sources, and compatibility can concern compilation, runtime linkage, modules, reflection, annotation processing, serialization, native interop, or mixed-language consumers.

Classpath order, duplicate classes, service descriptors, automatic and explicit modules, exports, opens, and reads, reflection, method handles, serializers, dependency injection, annotation processors, compiler plugins, JNI, and dynamically loaded agents govern what actually runs. Versions and toolchains are also owned indirectly, so ownership changes can reach:

- wrappers, toolchain files, and settings
- parent POMs, convention plugins, version catalogs, dependency-management blocks, and imported BOMs
- repositories and caches
- shading, packaging, and launch scripts

Build and runtime evidence spans dependency resolution, compilation, tests, packaging, and launch through the repository's configured wrapper and JDK for each affected supported variant, and a compile classpath does not prove the runtime classpath. Dependency explanations, module resolution, packaged contents, service merging, generated outputs, and representative downstream consumers are artifact evidence where binary or reflective behavior is at risk. Behavioral evidence covers startup, linkage, reflection, annotation processing, serialization, native loading, mixed Java, Kotlin, and Groovy interoperation, and concurrency on the intended runtime, and a change must preserve reproducibility and locked dependency ownership unless altering them is part of its requested outcome.
