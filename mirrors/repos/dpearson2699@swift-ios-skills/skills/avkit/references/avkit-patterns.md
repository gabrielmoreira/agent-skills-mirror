# AVKit Patterns

Advanced patterns for AVKit media playback beyond the main skill coverage.

## Contents

- [Custom Player UI with AVPlayerLayer](#custom-player-ui-with-avplayerlayer)
- [Interstitial Content](#interstitial-content)
- [Background Playback](#background-playback)
- [Error Handling](#error-handling)
- [Observing Playback State](#observing-playback-state)
- [Video Frame Analysis](#video-frame-analysis)
- [HDR Content](#hdr-content)
- [SwiftUI Player Manager](#swiftui-player-manager)
- [AVPlayerViewController in UIViewControllerRepresentable](#avplayerviewcontroller-in-uiviewcontrollerrepresentable)

## Custom Player UI with AVPlayerLayer

When `AVPlayerViewController` does not meet your design requirements, build a
custom player UI using `AVPlayerLayer` directly. You lose system transport
controls but gain full control over the interface.

```swift
import AVFoundation
import UIKit

final class CustomPlayerView: UIView {
    override class var layerClass: AnyClass { AVPlayerLayer.self }

    var playerLayer: AVPlayerLayer { layer as! AVPlayerLayer }

    var player: AVPlayer? {
        get { playerLayer.player }
        set { playerLayer.player = newValue }
    }

    override init(frame: CGRect) {
        super.init(frame: frame)
        playerLayer.videoGravity = .resizeAspect
    }

    required init?(coder: NSCoder) {
        super.init(coder: coder)
        playerLayer.videoGravity = .resizeAspect
    }
}
```

### Adding PiP to a Custom Player

Use `AVPictureInPictureController` with the custom player layer:

```swift
import AVKit

final class CustomPlayerController: UIViewController, AVPictureInPictureControllerDelegate {
    private let playerView = CustomPlayerView()
    private var pipController: AVPictureInPictureController?
    private let player = AVPlayer()

    override func viewDidLoad() {
        super.viewDidLoad()
        view.addSubview(playerView)
        playerView.player = player

        if AVPictureInPictureController.isPictureInPictureSupported() {
            pipController = AVPictureInPictureController(playerLayer: playerView.playerLayer)
            pipController?.delegate = self
            pipController?.canStartPictureInPictureAutomaticallyFromInline = true
        }
    }

    func play(url: URL) {
        player.replaceCurrentItem(with: AVPlayerItem(url: url))
        player.play()
    }

    // MARK: - AVPictureInPictureControllerDelegate

    func pictureInPictureControllerWillStartPictureInPicture(
        _ pictureInPictureController: AVPictureInPictureController
    ) {
        // Prepare UI for PiP (e.g., hide custom controls)
    }

    func pictureInPictureControllerDidStopPictureInPicture(
        _ pictureInPictureController: AVPictureInPictureController
    ) {
        // Restore custom controls
    }

    func pictureInPictureController(
        _ pictureInPictureController: AVPictureInPictureController,
        restoreUserInterfaceForPictureInPictureStopWithCompletionHandler completionHandler: @escaping (Bool) -> Void
    ) {
        // Re-present the player view controller
        completionHandler(true)
    }
}
```

### PiP with Sample Buffers

For apps rendering video frames manually (e.g., from a custom pipeline), use
the sample buffer content source:

```swift
import AVKit

func setupSampleBufferPiP(
    displayLayer: AVSampleBufferDisplayLayer,
    delegate: AVPictureInPictureSampleBufferPlaybackDelegate
) -> AVPictureInPictureController? {
    guard AVPictureInPictureController.isPictureInPictureSupported() else { return nil }

    let contentSource = AVPictureInPictureController.ContentSource(
        sampleBufferDisplayLayer: displayLayer,
        playbackDelegate: delegate
    )
    let controller = AVPictureInPictureController(contentSource: contentSource)
    return controller
}
```

The playback delegate must report timing and play/pause state:

```swift
final class SampleBufferPlaybackHandler: NSObject, AVPictureInPictureSampleBufferPlaybackDelegate {
    var isPlaying = true
    var currentTime: CMTime = .zero
    var duration: CMTime = CMTime(seconds: 300, preferredTimescale: 600)

    func pictureInPictureController(
        _ pictureInPictureController: AVPictureInPictureController,
        setPlaying playing: Bool
    ) {
        isPlaying = playing
    }

    func pictureInPictureControllerTimeRangeForPlayback(
        _ pictureInPictureController: AVPictureInPictureController
    ) -> CMTimeRange {
        CMTimeRange(start: .zero, duration: duration)
    }

    func pictureInPictureControllerIsPlaybackPaused(
        _ pictureInPictureController: AVPictureInPictureController
    ) -> Bool {
        !isPlaying
    }

    func pictureInPictureController(
        _ pictureInPictureController: AVPictureInPictureController,
        didTransitionToRenderSize newRenderSize: CMVideoDimensions
    ) {
        // Adjust rendering resolution for PiP window size
    }

    func pictureInPictureController(
        _ pictureInPictureController: AVPictureInPictureController,
        skipByInterval skipInterval: CMTime,
        completion: @escaping () -> Void
    ) {
        currentTime = CMTimeAdd(currentTime, skipInterval)
        completion()
    }

    func pictureInPictureControllerShouldProhibitBackgroundAudioPlayback(
        _ pictureInPictureController: AVPictureInPictureController
    ) -> Bool {
        false
    }
}
```

## Interstitial Content

Mark time ranges in the media timeline as interstitial (ads, legal notices).
The player dims these ranges in the scrubber and can enforce linear playback
during them.

### AVInterstitialTimeRange (tvOS / iOS)

```swift
import AVKit
import CoreMedia

func configureInterstitials(for playerItem: AVPlayerItem) {
    let adStart = CMTime(seconds: 30, preferredTimescale: 600)
    let adDuration = CMTime(seconds: 15, preferredTimescale: 600)
    let adRange = CMTimeRange(start: adStart, duration: adDuration)

    let interstitial = AVInterstitialTimeRange(timeRange: adRange)

    // Add a second ad break
    let secondAdStart = CMTime(seconds: 120, preferredTimescale: 600)
    let secondAdDuration = CMTime(seconds: 30, preferredTimescale: 600)
    let secondAdRange = CMTimeRange(start: secondAdStart, duration: secondAdDuration)
    let secondInterstitial = AVInterstitialTimeRange(timeRange: secondAdRange)

    playerItem.interstitialTimeRanges = [interstitial, secondInterstitial]
}
```

### Server-Side Ad Insertion with AVPlayerInterstitialEventController

For HLS streams with server-side ad insertion, use `AVPlayerInterstitialEventController`
from AVFoundation:

```swift
import AVFoundation

func setupInterstitialEvents(primaryPlayer: AVPlayer) {
    let controller = AVPlayerInterstitialEventController(primaryPlayer: primaryPlayer)

    let adAsset = AVURLAsset(url: URL(string: "https://example.com/ad.m3u8")!)
    let adItem = AVPlayerItem(asset: adAsset)

    let event = AVPlayerInterstitialEvent(
        primaryItem: primaryPlayer.currentItem!,
        time: CMTime(seconds: 60, preferredTimescale: 600)
    )
    event.templateItems = [adItem]
    event.restrictions = [.requiresPlaybackAtPreferredRateForAdvancement]

    controller.events = [event]
}
```

### Delegate Callbacks for Interstitials

```swift
func playerViewController(
    _ playerViewController: AVPlayerViewController,
    willPresent interstitial: AVInterstitialTimeRange
) {
    // About to play interstitial content — disable skip controls
    playerViewController.requiresLinearPlayback = true
}

func playerViewController(
    _ playerViewController: AVPlayerViewController,
    didPresent interstitial: AVInterstitialTimeRange
) {
    // Interstitial finished — re-enable seeking
    playerViewController.requiresLinearPlayback = false
}
```

## Background Playback

### Info.plist Configuration

Add the `audio` background mode:

```xml
<key>UIBackgroundModes</key>
<array>
    <string>audio</string>
</array>
```

### Handling App Lifecycle

The system pauses video upon scene backgrounding automatically. For audio-only
background playback (e.g., a podcast app with video), detach the player from
the view layer:

```swift
func sceneDidEnterBackground(_ scene: UIScene) {
    // Remove the player from the view layer to continue audio-only playback
    playerVC.player = nil
    // Keep a strong reference to the AVPlayer to prevent deallocation
}

func sceneWillEnterForeground(_ scene: UIScene) {
    // Re-attach the player
    playerVC.player = player
}
```

### Preventing Background Pause

If PiP is active when the app backgrounds, playback continues in the PiP
window. Without PiP, audio-only playback requires removing the player layer
as shown above, and the audio session must be `.playback`.

## Error Handling

### Observing Player Item Status

```swift
func observePlayerItem(_ item: AVPlayerItem) {
    let observation = item.observe(\.status) { item, _ in
        switch item.status {
        case .readyToPlay:
            // Safe to begin playback
            break
        case .failed:
            if let error = item.error as? NSError {
                handlePlaybackError(error)
            }
        case .unknown:
            break
        @unknown default:
            break
        }
    }
}

func handlePlaybackError(_ error: NSError) {
    switch error.domain {
    case NSURLErrorDomain:
        // Network-related errors
        if error.code == NSURLErrorNotConnectedToInternet {
            // Show offline message
        } else if error.code == NSURLErrorTimedOut {
            // Offer retry
        }
    case AVFoundationErrorDomain:
        // AVFoundation-specific errors
        break
    default:
        break
    }
}
```

### Observing Player Time Control Status

```swift
func observePlayer(_ player: AVPlayer) {
    let observation = player.observe(\.timeControlStatus) { player, _ in
        switch player.timeControlStatus {
        case .paused:
            break
        case .playing:
            break
        case .waitingToPlayAtSpecifiedRate:
            if let reason = player.reasonForWaitingToPlay {
                switch reason {
                case .toMinimizeStalls:
                    // Buffering — show spinner
                    break
                case .evaluatingBufferingRate:
                    break
                case .noItemToPlay:
                    break
                default:
                    break
                }
            }
        @unknown default:
            break
        }
    }
}
```

### Handling AVKitError

```swift
import AVKit

func handleAVKitError(_ error: Error) {
    guard let avkitError = error as? AVKitError else { return }

    switch avkitError.code {
    case .pictureInPictureStartFailed:
        // PiP could not start — check audio session and entitlements
        break
    case .contentRatingUnknown:
        // Content rating could not be determined
        break
    case .contentDisallowedByPasscode:
        // Parental controls restrict this content
        break
    case .contentDisallowedByProfile:
        // MDM profile restricts this content
        break
    case .unknown:
        break
    @unknown default:
        break
    }
}
```

## Observing Playback State

### Periodic Time Observer

```swift
func addPeriodicObserver(to player: AVPlayer) -> Any {
    let interval = CMTime(seconds: 0.5, preferredTimescale: 600)
    return player.addPeriodicTimeObserver(forInterval: interval, queue: .main) { time in
        let seconds = CMTimeGetSeconds(time)
        // Update progress UI
    }
}

// Remove when done
// player.removeTimeObserver(observer)
```

### Boundary Time Observer

Trigger actions at specific points in the timeline:

```swift
func addBoundaryObserver(to player: AVPlayer, at times: [CMTime]) -> Any {
    let timeValues = times.map { NSValue(time: $0) }
    return player.addBoundaryTimeObserver(forTimes: timeValues, queue: .main) {
        // Reached a boundary time
    }
}
```

### Observing Playback End

```swift
func observePlaybackEnd(for item: AVPlayerItem) {
    NotificationCenter.default.addObserver(
        forName: .AVPlayerItemDidPlayToEndTime,
        object: item,
        queue: .main
    ) { _ in
        // Playback finished — show replay button or load next item
    }
}
```

## Video Frame Analysis

`AVPlayerViewController` supports automatic analysis of paused video frames
for text recognition, visual search, and subject lifting.

```swift
let playerVC = AVPlayerViewController()

// Enable frame analysis (default is true)
playerVC.allowsVideoFrameAnalysis = true

// Configure which analysis types to perform
playerVC.videoFrameAnalysisTypes = [.text, .visualSearch, .subject, .machineReadableCode]
```

## HDR Content

Control how HDR video content renders:

```swift
// Let the system decide the best rendering
playerVC.preferredDisplayDynamicRange = .automatic

// Force SDR rendering
playerVC.preferredDisplayDynamicRange = .standard

// Full HDR
playerVC.preferredDisplayDynamicRange = .high

// Constrained HDR (tone-mapped HDR)
playerVC.preferredDisplayDynamicRange = .constrainedHigh
```

## SwiftUI Player Manager

An `@Observable` manager for coordinating playback state across a SwiftUI app:

```swift
import AVKit
import AVFoundation

@Observable
@MainActor
final class VideoPlayerManager {
    private(set) var player: AVPlayer?
    private(set) var isPlaying = false
    private(set) var currentTime: TimeInterval = 0
    private(set) var duration: TimeInterval = 0
    private(set) var isBuffering = false
    private(set) var error: Error?

    private var timeObserver: Any?
    private var statusObservation: NSKeyValueObservation?
    private var timeControlObservation: NSKeyValueObservation?

    func loadMedia(url: URL) {
        cleanup()

        let item = AVPlayerItem(url: url)
        let newPlayer = AVPlayer(playerItem: item)
        player = newPlayer

        observeStatus(of: item)
        observeTimeControl(of: newPlayer)
        addPeriodicTimeObserver(to: newPlayer)
    }

    func play() {
        player?.play()
    }

    func pause() {
        player?.pause()
    }

    func seek(to time: TimeInterval) {
        let cmTime = CMTime(seconds: time, preferredTimescale: 600)
        player?.seek(to: cmTime, toleranceBefore: .zero, toleranceAfter: .zero)
    }

    func cleanup() {
        if let observer = timeObserver, let player {
            player.removeTimeObserver(observer)
        }
        timeObserver = nil
        statusObservation?.invalidate()
        timeControlObservation?.invalidate()
        player = nil
        error = nil
        isPlaying = false
        currentTime = 0
        duration = 0
    }

    private func observeStatus(of item: AVPlayerItem) {
        statusObservation = item.observe(\.status) { [weak self] item, _ in
            Task { @MainActor in
                guard let self else { return }
                switch item.status {
                case .readyToPlay:
                    self.duration = CMTimeGetSeconds(item.duration)
                case .failed:
                    self.error = item.error
                case .unknown:
                    break
                @unknown default:
                    break
                }
            }
        }
    }

    private func observeTimeControl(of player: AVPlayer) {
        timeControlObservation = player.observe(\.timeControlStatus) { [weak self] player, _ in
            Task { @MainActor in
                guard let self else { return }
                self.isPlaying = player.timeControlStatus == .playing
                self.isBuffering = player.timeControlStatus == .waitingToPlayAtSpecifiedRate
            }
        }
    }

    private func addPeriodicTimeObserver(to player: AVPlayer) {
        let interval = CMTime(seconds: 0.5, preferredTimescale: 600)
        timeObserver = player.addPeriodicTimeObserver(forInterval: interval, queue: .main) { [weak self] time in
            Task { @MainActor in
                self?.currentTime = CMTimeGetSeconds(time)
            }
        }
    }

    deinit {
        if let observer = timeObserver, let player {
            player.removeTimeObserver(observer)
        }
    }
}
```

### Using the Manager in SwiftUI

```swift
import SwiftUI
import AVKit

struct VideoScreen: View {
    @State private var manager = VideoPlayerManager()

    var body: some View {
        VStack {
            if let player = manager.player {
                VideoPlayer(player: player)
                    .frame(height: 300)

                HStack {
                    Button(manager.isPlaying ? "Pause" : "Play") {
                        manager.isPlaying ? manager.pause() : manager.play()
                    }

                    Text("\(Int(manager.currentTime))s / \(Int(manager.duration))s")
                }
            }

            if manager.isBuffering {
                ProgressView("Buffering...")
            }

            if let error = manager.error {
                Text("Error: \(error.localizedDescription)")
                    .foregroundStyle(.red)
            }
        }
        .task {
            manager.loadMedia(url: URL(string: "https://example.com/video.m3u8")!)
        }
    }
}
```

## AVPlayerViewController in UIViewControllerRepresentable

Full-featured wrapper exposing delegate callbacks, PiP, and playback speed to
SwiftUI. Prefer this over `VideoPlayer` when you need fine-grained control.

```swift
import SwiftUI
import AVKit

struct SystemPlayerView: UIViewControllerRepresentable {
    let player: AVPlayer
    var allowsPiP: Bool = true
    var autoStartPiPFromInline: Bool = false
    var speeds: [AVPlaybackSpeed] = AVPlaybackSpeed.systemDefaultSpeeds

    func makeUIViewController(context: Context) -> AVPlayerViewController {
        let controller = AVPlayerViewController()
        controller.player = player
        controller.allowsPictureInPicturePlayback = allowsPiP
        controller.canStartPictureInPictureAutomaticallyFromInline = autoStartPiPFromInline
        controller.speeds = speeds
        controller.delegate = context.coordinator
        return controller
    }

    func updateUIViewController(_ controller: AVPlayerViewController, context: Context) {
        controller.player = player
    }

    func makeCoordinator() -> Coordinator { Coordinator() }

    final class Coordinator: NSObject, AVPlayerViewControllerDelegate {
        func playerViewController(
            _ playerViewController: AVPlayerViewController,
            willBeginFullScreenPresentationWithAnimationCoordinator coordinator: any UIViewControllerTransitionCoordinator
        ) {
            // Handle full-screen entry
        }

        func playerViewController(
            _ playerViewController: AVPlayerViewController,
            willEndFullScreenPresentationWithAnimationCoordinator coordinator: any UIViewControllerTransitionCoordinator
        ) {
            // Handle full-screen exit
        }

        func playerViewController(
            _ playerViewController: AVPlayerViewController,
            restoreUserInterfaceForPictureInPictureStopWithCompletionHandler completionHandler: @escaping (Bool) -> Void
        ) {
            completionHandler(true)
        }

        func playerViewController(
            _ playerViewController: AVPlayerViewController,
            failedToStartPictureInPictureWithError error: any Error
        ) {
            print("PiP failed: \(error)")
        }
    }
}
```
