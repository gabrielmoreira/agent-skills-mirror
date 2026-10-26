import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15

Rectangle {
    id: rootPanel
    width: 400
    height: 300
    color: "#0f172a"
    radius: 8
    border.color: "#1e293b"
    border.width: 1

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 12

        Label {
            text: "Sensory Stream Telemetry"
            color: "#f8fafc"
            font.pixelSize: 18
            font.bold: true
        }

        Button {
            text: "Acknowledge Signal"
            Layout.fillWidth: true
            onClicked: console.log("Signal acknowledged.")
        }
    }
}
