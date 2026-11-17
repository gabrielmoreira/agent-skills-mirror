/* Editable Canvas helpers. Every draw derives its result from the supplied time. */
(function (root) {
  'use strict';

  const clamp = value => Math.max(0, Math.min(1, value));
  function randomAt(x, y, seed = 1) {
    let value = Math.imul(x + seed, 374761393) + Math.imul(y, 668265263);
    value = Math.imul(value ^ (value >>> 13), 1274126177);
    return ((value ^ (value >>> 16)) >>> 0) / 4294967296;
  }
  function between(range, amount) {
    return range[0] + (range[1] - range[0]) * amount;
  }
  function sampleKeys(keys, time) {
    if (time <= keys[0][0]) return keys[0].slice(1);
    for (let index = 1; index < keys.length; index++) {
      if (time <= keys[index][0]) {
        const previous = keys[index - 1];
        const current = keys[index];
        const amount = (time - previous[0]) / (current[0] - previous[0]);
        return previous.slice(1).map((value, axis) => value + (current[axis + 1] - value) * amount);
      }
    }
    return keys[keys.length - 1].slice(1);
  }
  function surface(width, height) {
    const canvas = root.document.createElement('canvas');
    canvas.width = Math.max(1, Math.ceil(width));
    canvas.height = Math.max(1, Math.ceil(height));
    return canvas;
  }
  function dimensions(image) {
    const width = image.naturalWidth || image.width;
    const height = image.naturalHeight || image.height;
    if (!(width > 0 && height > 0)) throw new Error('Load the source image before creating a layer.');
    return [width, height];
  }

  function createTextureLayer(options) {
    const { image, box, mask, motion, velocity = [0, 0], offset = [0, 0], timeOrigin = 0,
      scale = 1, wrapX = false, wrapY = false, resolution = 1,
      edgeFade = [0, 0, 0, 0], composite } = options;
    const [imageWidth, imageHeight] = dimensions(image);
    if (!(box[2] > 0 && box[3] > 0 && scale > 0 && resolution > 0)) throw new Error('Layer dimensions and scale must be positive.');
    const canvas = surface(box[2] * resolution, box[3] * resolution);
    const context = canvas.getContext('2d');
    const width = imageWidth * scale;
    const height = imageHeight * scale;
    let coverage;
    if (mask || edgeFade.some(value => value > 0)) {
      coverage = surface(canvas.width, canvas.height);
      const alpha = coverage.getContext('2d');
      alpha.scale(resolution, resolution);
      if (mask) alpha.drawImage(mask, 0, 0, box[2], box[3]);
      else {
        alpha.fillStyle = 'white';
        alpha.fillRect(0, 0, box[2], box[3]);
      }
      const [left, top, right, bottom] = edgeFade;
      const fades = [
        [left, 0, 0, left, 0],
        [top, 0, 0, 0, top],
        [right, box[2], 0, box[2] - right, 0],
        [bottom, 0, box[3], 0, box[3] - bottom],
      ];
      alpha.globalCompositeOperation = 'destination-in';
      for (const [distance, x0, y0, x1, y1] of fades) {
        if (!(distance > 0)) continue;
        const gradient = alpha.createLinearGradient(x0, y0, x1, y1);
        gradient.addColorStop(0, 'transparent');
        gradient.addColorStop(1, 'white');
        alpha.fillStyle = gradient;
        alpha.fillRect(0, 0, box[2], box[3]);
      }
    }
    return {
      draw(destination, time, opacity = 1) {
        const position = motion ? sampleKeys(motion, time) : velocity.map(value => value * (time - timeOrigin));
        let x = offset[0] + position[0];
        let y = offset[1] + position[1];
        if (wrapX) x = ((x % width) + width) % width - width;
        if (wrapY) y = ((y % height) + height) % height - height;
        context.setTransform(resolution, 0, 0, resolution, 0, 0);
        context.clearRect(0, 0, box[2], box[3]);
        const columns = wrapX ? Math.ceil(box[2] / width) + 2 : 1;
        const rows = wrapY ? Math.ceil(box[3] / height) + 2 : 1;
        for (let row = 0; row < rows; row++) {
          for (let column = 0; column < columns; column++) {
            context.drawImage(image, x + column * width, y + row * height, width, height);
          }
        }
        if (coverage) {
          context.globalCompositeOperation = 'destination-in';
          context.drawImage(coverage, 0, 0, box[2], box[3]);
          context.globalCompositeOperation = 'source-over';
        }
        destination.save();
        destination.globalAlpha *= clamp(opacity);
        if (composite) destination.globalCompositeOperation = composite;
        destination.drawImage(canvas, ...box);
        destination.restore();
      },
    };
  }

  function createParticleField(options) {
    const { image, sprite, box, pitch = 6, density = 0.18, threshold = 0.04, seed = 1,
      size = [3, 7], release = [0, 0.5], lifetime = [0.8, 1.8], speed = [40, 100],
      acceleration = 80, origin = [box[2] / 2, box[3] / 2], trail = 0.025, samples = 3,
      fadeIn = 0.06, fadeOut = 0.4, sizeGrowth = 0.3, composite = 'lighter',
      dissolve = true, softness = 0.08, spriteMatte = 'black', preserveEnergy = true } = options;
    if (!(pitch > 0 && box[2] > 0 && box[3] > 0 && lifetime[0] > 0 && samples >= 1)) throw new Error('Particle dimensions, lifetime and sample count must be positive.');
    if (!Number.isInteger(samples)) throw new Error('Particle sample count must be an integer.');
    if (!sprite) throw new Error('Supply a source-derived particle sprite.');
    if (!['black', 'white', 'alpha'].includes(spriteMatte)) throw new Error('spriteMatte must be black, white or alpha.');
    const [imageWidth, imageHeight] = dimensions(image);
    const [spriteWidth, spriteHeight] = dimensions(sprite);
    const source = surface(imageWidth, imageHeight);
    const sourceContext = source.getContext('2d', { willReadFrequently: true });
    sourceContext.drawImage(image, 0, 0);
    const pixels = sourceContext.getImageData(0, 0, imageWidth, imageHeight).data;
    const spriteCanvas = surface(spriteWidth, spriteHeight);
    const spriteContext = spriteCanvas.getContext('2d', { willReadFrequently: true });
    spriteContext.drawImage(sprite, 0, 0);
    const spritePixels = spriteContext.getImageData(0, 0, spriteWidth, spriteHeight);
    // Unmatte source pixels while preserving their internal colour. Reapplying
    // the recovered alpha over the original matte reproduces the source sprite.
    for (let index = 0; index < spritePixels.data.length; index += 4) {
      const red = spritePixels.data[index], green = spritePixels.data[index + 1], blue = spritePixels.data[index + 2];
      const coverage = spriteMatte === 'alpha' ? 1 : spriteMatte === 'white'
        ? 1 - Math.min(red, green, blue) / 255 : Math.max(red, green, blue) / 255;
      spritePixels.data[index + 3] *= coverage;
      for (let channel = 0; channel < 3; channel++) {
        const background = spriteMatte === 'white' ? (1 - coverage) * 255 : 0;
        spritePixels.data[index + channel] = coverage > 0 ? (spritePixels.data[index + channel] - background) / coverage : 0;
      }
    }
    const tintedSprites = new Map();
    function colouredSprite(red, green, blue) {
      const colour = [red, green, blue].map(value => Math.min(255, Math.round(value / 32) * 32));
      const key = colour.join(',');
      if (!tintedSprites.has(key)) {
        const canvas = surface(spriteWidth, spriteHeight);
        const context = canvas.getContext('2d');
        const tinted = context.createImageData(spriteWidth, spriteHeight);
        tinted.data.set(spritePixels.data);
        let energy = 0;
        for (let index = 0; index < tinted.data.length; index += 4) {
          for (let channel = 0; channel < 3; channel++) tinted.data[index + channel] *= colour[channel] / 255;
          const strength = threshold > 0
            ? (.299 * tinted.data[index] + .587 * tinted.data[index + 1] + .114 * tinted.data[index + 2]) / 255 : 1;
          energy += strength * tinted.data[index + 3] / 255;
        }
        context.putImageData(tinted, 0, 0);
        tintedSprites.set(key, { canvas, energyPerSquaredWidth: energy / (spriteWidth * spriteWidth) });
      }
      return tintedSprites.get(key);
    }
    const columns = Math.ceil(box[2] / pitch);
    const rows = Math.ceil(box[3] / pitch);
    const cellEnergy = new Float64Array(columns * rows);
    if (preserveEnergy) {
      const scaleX = box[2] / imageWidth, scaleY = box[3] / imageHeight;
      for (let y = 0; y < imageHeight; y++) {
        const row = Math.min(rows - 1, Math.floor((y + 0.5) * scaleY / pitch));
        for (let x = 0; x < imageWidth; x++) {
          const column = Math.min(columns - 1, Math.floor((x + 0.5) * scaleX / pitch));
          const index = (y * imageWidth + x) * 4;
          const strength = threshold > 0
            ? (.299 * pixels[index] + .587 * pixels[index + 1] + .114 * pixels[index + 2]) / 255 : 1;
          cellEnergy[row * columns + column] += strength * pixels[index + 3] / 255 * scaleX * scaleY;
        }
      }
    }
    const mask = surface(columns, rows);
    const maskContext = mask.getContext('2d');
    const maskPixels = maskContext.createImageData(columns, rows);
    const intact = surface(box[2], box[3]);
    const intactContext = intact.getContext('2d');
    const exposure = composite === 'source-over' && samples > 1 ? surface(1, 1) : null;
    const exposureContext = exposure && exposure.getContext('2d');
    const cells = [];
    const particles = [];
    for (let row = 0; row < rows; row++) {
      for (let column = 0; column < columns; column++) {
        const x = Math.min(box[2] - 0.5, (column + 0.5) * pitch);
        const y = Math.min(box[3] - 0.5, (row + 0.5) * pitch);
        const cluster = randomAt(Math.floor(column / 3), Math.floor(row / 3), seed);
        const releasedAt = between(release, cluster * 0.7 + randomAt(column, row, seed + 1) * 0.3);
        cells.push(releasedAt);
        const sourceX = Math.min(imageWidth - 1, Math.floor(x / box[2] * imageWidth));
        const sourceY = Math.min(imageHeight - 1, Math.floor(y / box[3] * imageHeight));
        const index = (sourceY * imageWidth + sourceX) * 4;
        const [red, green, blue, alpha] = pixels.subarray(index, index + 4);
        if (alpha === 0 || Math.max(red, green, blue) / 255 < threshold || randomAt(column, row, seed + 2) > density) continue;
        const dx = x - origin[0];
        const dy = y - origin[1];
        const length = Math.hypot(dx, dy) || 1;
        const travelSpeed = between(speed, randomAt(column, row, seed + 3));
        const appearance = colouredSprite(red, green, blue);
        particles.push({
          x, y, release: releasedAt, alpha: alpha / 255,
          energy: cellEnergy[row * columns + column], unitEnergy: appearance.energyPerSquaredWidth,
          life: between(lifetime, randomAt(column, row, seed + 4)),
          size: between(size, randomAt(column, row, seed + 5)),
          vx: dx / length * travelSpeed, vy: dy / length * travelSpeed,
          ax: dx / length * acceleration, ay: dy / length * acceleration,
          sprite: appearance.canvas,
        });
      }
    }
    return {
      count: particles.length,
      draw(destination, time, opacity = 1) {
        destination.save();
        destination.translate(box[0], box[1]);
        destination.globalAlpha *= clamp(opacity);
        if (dissolve) {
          for (let index = 0; index < cells.length; index++) {
            const alpha = softness > 0 ? clamp((cells[index] - time) / softness + 0.5) : Number(time < cells[index]);
            const pixel = index * 4;
            maskPixels.data[pixel] = maskPixels.data[pixel + 1] = maskPixels.data[pixel + 2] = 255;
            maskPixels.data[pixel + 3] = Math.round(alpha * 255);
          }
          maskContext.putImageData(maskPixels, 0, 0);
          intactContext.clearRect(0, 0, box[2], box[3]);
          intactContext.drawImage(image, 0, 0, box[2], box[3]);
          intactContext.globalCompositeOperation = 'destination-in';
          intactContext.drawImage(mask, 0, 0, box[2], box[3]);
          intactContext.globalCompositeOperation = 'source-over';
          destination.drawImage(intact, 0, 0);
        }
        destination.globalCompositeOperation = composite;
        const parentAlpha = destination.globalAlpha;
        for (const particle of particles) {
          const age = time - particle.release;
          if (age < 0 || age >= particle.life) continue;
          const entrance = fadeIn > 0 ? clamp(age / fadeIn) : 1;
          const exit = fadeOut > 0 ? clamp((particle.life - age) / fadeOut) : 1;
          const width = particle.size * (1 + age * sizeGrowth);
          const height = width * spriteHeight / spriteWidth;
          const energyOpacity = particle.unitEnergy > 0 ? particle.energy / (particle.unitEnergy * width * width) : 0;
          const alpha = preserveEnergy ? Math.min(particle.alpha, energyOpacity) : particle.alpha;
          const released = preserveEnergy && dissolve && softness > 0 ? clamp(age / softness + 0.5) : 1;
          const particleAlpha = parentAlpha * alpha * released * entrance * exit;
          const positions = [];
          for (let sample = 0; sample < samples; sample++) {
            const dt = samples > 1 ? (sample / (samples - 1) - 0.5) * trail : 0;
            const sampleAge = Math.max(0, Math.min(particle.life, age + dt));
            const x = particle.x + particle.vx * sampleAge + particle.ax * sampleAge * sampleAge / 2;
            const y = particle.y + particle.vy * sampleAge + particle.ay * sampleAge * sampleAge / 2;
            positions.push([x - width / 2, y - height / 2]);
          }
          if (exposure) {
            // Source-over samples do not add opacity. Average premultiplied
            // colour/alpha separately, then composite this particle only once.
            const left = Math.floor(Math.min(...positions.map(position => position[0])));
            const top = Math.floor(Math.min(...positions.map(position => position[1])));
            const right = Math.ceil(Math.max(...positions.map(position => position[0])) + width);
            const bottom = Math.ceil(Math.max(...positions.map(position => position[1])) + height);
            if (exposure.width !== right - left) exposure.width = right - left;
            if (exposure.height !== bottom - top) exposure.height = bottom - top;
            exposureContext.clearRect(0, 0, exposure.width, exposure.height);
            exposureContext.globalCompositeOperation = 'lighter';
            exposureContext.globalAlpha = 1 / samples;
            for (const [x, y] of positions) exposureContext.drawImage(particle.sprite, x - left, y - top, width, height);
            destination.globalAlpha = particleAlpha;
            destination.drawImage(exposure, left, top);
          } else {
            destination.globalAlpha = particleAlpha / samples;
            for (const [x, y] of positions) destination.drawImage(particle.sprite, x, y, width, height);
          }
        }
        destination.restore();
      },
    };
  }

  root.OpenMotionReconstruction = Object.freeze({ createTextureLayer, createParticleField });
})(globalThis);
