# Social Asset Production Checklist

## Common Placements

- Profile picture or avatar
- Header, banner, or cover image
- Feed post image
- Article, newsletter, or link cover
- Thumbnail
- Carousel slide
- Short-video cover frame
- Story or vertical post

## Export Review

- Size and aspect ratio match the intended placement.
- Important text and faces are inside a conservative safe area.
- Small preview is legible at feed and thumbnail sizes.
- Circle crop preview works for profile pictures.
- Banner preview accounts for profile image overlap and responsive cropping.
- Dark and light UI contexts do not break contrast.
- Alt text or descriptive caption is prepared where useful.
- Source prompts, references, and rights notes are retained.

## Current Platform Notes To Verify

These facts were checked against official docs during May 2026 work, but should
be re-verified before exact recommendations:

- X recommends 1500 x 500 for header images and 400 x 400 for profile images.
- X supports JPG, GIF, and PNG for profile/header images, but animated GIFs are
  not supported for those surfaces.
- Facebook Page profile pictures are circular and should be 320 x 320 for best
  quality. Facebook says PNG can work better for profile or cover images with
  logos or text.
- Facebook Page cover photos are left-aligned, full-bleed 16:9, can be cropped
  or resized, and Facebook lists 851 x 315 JPG under 100 KB as a fast-loading
  option.
- YouTube Shorts uses square or vertical video. Covers should keep the main
  visual and text inside mobile-safe regions because UI overlays vary.

## Naming Pattern

Use descriptive filenames:

```text
brand-platform-placement-concept-widthxheight-variant.ext
```

Examples:

- `ironfieldops-x-header-custom-ai-1500x500.png`
- `agentskills-facebook-post-launch-1080x1350.png`
- `ironfieldops-youtube-short-cover-workflow-1080x1920.jpg`
