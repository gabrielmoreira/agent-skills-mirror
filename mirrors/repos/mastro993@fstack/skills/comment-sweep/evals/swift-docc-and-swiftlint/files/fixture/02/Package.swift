// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "FieldNotes",
    platforms: [.iOS(.v17), .macOS(.v14)],
    products: [
        .library(name: "FieldNotes", targets: ["FieldNotes"]),
    ],
    targets: [
        .target(name: "FieldNotes"),
        .testTarget(name: "FieldNotesTests", dependencies: ["FieldNotes"]),
    ]
)
