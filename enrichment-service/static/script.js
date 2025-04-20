const tooltip = document.getElementById("tooltip");
const tooltipDetails = document.getElementById("tooltip_details");
const tooltipImage = document.getElementById("tooltip_image");
const loader = document.getElementById("loader");
const canvas = document.getElementById("mosaic");
const ctx = canvas.getContext("2d");

let tileMetadata = [];
let gridSize = 8;
let tileSize = 64;

async function drawMosaic(tileData, gridSizeInput) {
  gridSize = gridSizeInput;
  tileSize = Math.floor(canvas.width / gridSize);
  tileMetadata = tileData;

  for (let i = 0; i < tileData.length; i++) {
    const tile = tileData[i];
    const row = Math.floor(i / gridSize);
    const col = i % gridSize;
    const x = col * tileSize;
    const y = row * tileSize;

    try {
      const img = await loadImage(tile.s3_path);
      ctx.drawImage(img, x, y, tileSize, tileSize);
    } catch (err) {
      const c = tile.average_color;
      ctx.fillStyle = `rgb(${c.r}, ${c.g}, ${c.b})`;
      ctx.fillRect(x, y, tileSize, tileSize);
    }
  }
}

function s3_to_https(url) {
  if (url.startsWith("s3://")) {
    const s3Parts = url.replace("s3://", "").split("/");
    const bucket = s3Parts.shift();
    const key = s3Parts.join("/");
    return `https://${bucket}.s3.amazonaws.com/${key}`;
  }
  return url;
}

function loadImage(url) {
  return new Promise((resolve, reject) => {
    // Convert s3://... to https://bucket.s3.amazonaws.com/key
    if (url.startsWith("s3://")) {
      url = s3_to_https(url);
    }

    const img = new Image();
    img.crossOrigin = "anonymous"; // still good practice
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = url;
  });
}

async function generateAndDrawMosaic() {
  const fileInput = document.getElementById("input_image");
  const file = fileInput.files[0];
  const sizeInput = parseInt(document.getElementById("mosaic_size").value, 10);
  if (!file || isNaN(sizeInput)) {
    alert("Please select an image and enter a valid mosaic size.");
    return;
  }

  const formData = new FormData();
  formData.append("image", file);
  formData.append("mosaic_size", sizeInput);

  loader.style.display = "block";

  try {
    const res = await fetch("/mosaic_generator", {
      method: "POST",
      body: formData
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Unknown error");
    }

    const data = await res.json();
    await drawMosaic(data.mosaic_tiles, sizeInput);
  } catch (e) {
    alert("Failed to generate mosaic: " + e.message);
  } finally {
    loader.style.display = "none";
  }
}

document.getElementById("submit").addEventListener("click", generateAndDrawMosaic);

// Tooltip behavior
canvas.addEventListener("mousemove", (e) => {
  const rect = canvas.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;

  const col = Math.floor(x / tileSize);
  const row = Math.floor(y / tileSize);
  const index = row * gridSize + col;

  if (tileMetadata[index]) {
    const tile = tileMetadata[index];
    tooltip.style.left = `${e.pageX + 10}px`;
    tooltip.style.top = `${e.pageY + 10}px`;
    tooltip.style.display = "block";
    tooltipDetails.innerHTML = `
      <strong>Source:</strong> ${tile.source}<br>
      <strong>Date:</strong> ${tile.date}<br>
      <strong>Classification:</strong> ${tile.classification}<br>
      <strong>R,G,B:</strong> ${tile.average_color.r}, ${tile.average_color.g}, ${tile.average_color.b}
    `;
    tooltipImage.src = tile.s3_path ? s3_to_https(tile.s3_path) : "";
  } else {
    tooltip.style.display = "none";
  }
});

canvas.addEventListener("mouseleave", () => {
  tooltip.style.display = "none";
});

// Open image on click
canvas.addEventListener("click", (e) => {
  const rect = canvas.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;

  const col = Math.floor(x / tileSize);
  const row = Math.floor(y / tileSize);
  const index = row * gridSize + col;

  if (tileMetadata[index]?.s3_path) {
    window.open(s3_to_https(tileMetadata[index].s3_path), "_blank");
  }
});