import sharp from 'sharp';

/**
 * Fetches a logo from a domain or URL and converts it to PNG.
 * @param {string} logoInput - Domain (e.g., 'google.com') or full URL.
 * @param {string} [clientId] - Brandfetch Client ID.
 * @returns {Promise<{ data: string, mimeType: string } | null>}
 */
export async function fetchLogo(logoInput, clientId) {
  let url;
  const headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8'
  };

  if (logoInput.startsWith('http://') || logoInput.startsWith('https://')) {
    url = logoInput;
  } else {
    // Assume it's a domain, use Brandfetch API
    url = `https://cdn.brandfetch.io/domain/${logoInput}/w/820/h/110/theme/dark/logo?c=${clientId}`;
  }

  try {
    let response;
    if (!logoInput.startsWith('http')) {
      try {
        response = await fetch(url, { headers });
      } catch (e) {
        response = { ok: false, headers: new Headers() };
      }

      let contentType = response.headers.get('content-type');
      if (!response.ok || !contentType?.includes('image')) {
        const hunterUrl = `https://logos.hunter.io/${logoInput}`;
        try {
          response = await fetch(hunterUrl, { headers });
        } catch (e) {
          response = { ok: false, headers: new Headers() };
        }

        contentType = response.headers.get('content-type');
        if (!response.ok || !contentType?.includes('image')) {
          const fallbackUrl = `https://icon.horse/icon/${logoInput}`;
          try {
            response = await fetch(fallbackUrl, { headers });
          } catch (e) {
            return null;
          }

          contentType = response.headers.get('content-type');
          if (!response.ok || !contentType?.includes('image')) {
            return null;
          }

          if (contentType === 'image/x-icon' || contentType === 'image/vnd.microsoft.icon') {
            throw new Error('Unsupported ICO format');
          }
        }
      }
    } else {
      response = await fetch(url, { headers });
      const contentType = response.headers.get('content-type');
      if (!response.ok || !contentType?.includes('image')) {
        return null;
      }
    }

    const arrayBuffer = await response.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);

    // Convert to PNG using sharp
    const pngBuffer = await sharp(buffer)
      .png()
      .toBuffer();

    const base64String = pngBuffer.toString('base64');

    return {
      data: base64String,
      mimeType: 'image/png'
    };
  } catch (error) {
    console.error(`Error fetching logo:`, error.message);
    return null;
  }
}
