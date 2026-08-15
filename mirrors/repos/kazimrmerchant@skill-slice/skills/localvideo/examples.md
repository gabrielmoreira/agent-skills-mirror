# localvideo — examples

```
/localvideo a drone over neon Tokyo at night
→ ASK duration; T2V OK (no likeness)

/localvideo 3s gpu-heavy cinematic empty concert stage, lasers, fog
→ draft/scenic T2V

/localimage 4x hero Michael Jackson on stage, fedora, white glove, sequined jacket, Pixar face close-up
→ approve best → refs/hero.png

/localvideo 3s best ref refs/hero.png same character moonwalk across stage, do not change face
→ I2V iterate until identity PASS

/localvideo 10s best ref refs/hero.png ...
→ ONLY after 3s PASS

/localvideo edit .\final\clip.mp4 upscale 1920
→ post
```

Anti-pattern (do not do for likeness finals):

```
/localvideo 10s Michael Jackson performing on stage
→ text-only long T2V — identity will fail (known failure mode)
```
