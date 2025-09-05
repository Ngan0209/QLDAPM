// slice_images.js
import images from "./images.js";

document.addEventListener("DOMContentLoaded", function () {
  const slides = document.getElementById("slides");

  // render ảnh
  images.forEach(src => {
    const img = document.createElement("img");
    img.src = src;
    img.style.width = "600px";
    img.style.height = "350px";
    img.style.objectFit = "cover";
    slides.appendChild(img);
  });

  let currentIndex = 0;

  function showSlide(index) {
    if (index < 0) currentIndex = images.length - 1;
    else if (index >= images.length) currentIndex = 0;
    else currentIndex = index;

    slides.style.transform = `translateX(${-600 * currentIndex}px)`;
  }

  document.querySelector(".next").addEventListener("click", () => showSlide(currentIndex + 1));
  document.querySelector(".prev").addEventListener("click", () => showSlide(currentIndex - 1));

  setInterval(() => showSlide(currentIndex + 1), 3000);
});
