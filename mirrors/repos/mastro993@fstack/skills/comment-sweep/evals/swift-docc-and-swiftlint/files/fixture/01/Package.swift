// swift-tools-version:5.7
import PackageDescription

let package = Package(
    name: "FieldNotes",
    platforms: [.iOS(.v16), .macOS(.v13)],
    products: [
        .library(name: "FieldNotes", targets: ["FieldNotes"]),
    ],
    targets: [
        .target(name: "FieldNotes"),
        .testTarget(name: "FieldNotesTests", dependencies: ["FieldNotes"]),
    ]
)
