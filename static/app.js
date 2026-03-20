const form = document.getElementById("recommend-form");
const movieInput = document.getElementById("movie-input");
const suggestions = document.getElementById("suggestions");
const resultPanel = document.getElementById("result-panel");
const resultTitle = document.getElementById("result-title");
const resultList = document.getElementById("result-list");
const errorPanel = document.getElementById("error-panel");

let debounceTimer;

function clearMessages() {
  errorPanel.hidden = true;
  errorPanel.textContent = "";
}

function showError(message) {
  resultPanel.hidden = true;
  errorPanel.hidden = false;
  errorPanel.textContent = message;
}

function showResults(movie, recommendations) {
  clearMessages();
  resultTitle.textContent = `Because you liked: ${movie}`;
  resultList.innerHTML = "";

  recommendations.forEach((title) => {
    const li = document.createElement("li");
    li.textContent = title;
    resultList.appendChild(li);
  });

  resultPanel.hidden = false;
}

async function fetchRecommendations(movie) {
  const response = await fetch(`/recommend?movie=${encodeURIComponent(movie)}`);
  const data = await response.json();

  if (!response.ok || data.error) {
    throw new Error(data.error || "Unable to get recommendations right now.");
  }

  return data;
}

function renderSuggestions(titles) {
  suggestions.innerHTML = "";

  titles.forEach((title) => {
    const item = document.createElement("li");
    item.textContent = title;
    item.setAttribute("role", "option");
    item.addEventListener("click", () => {
      movieInput.value = title;
      suggestions.innerHTML = "";
      movieInput.focus();
    });
    suggestions.appendChild(item);
  });
}

async function searchTitles(query) {
  const response = await fetch(`/search_titles?query=${encodeURIComponent(query)}`);
  const data = await response.json();
  if (!response.ok || !Array.isArray(data.titles)) {
    return [];
  }
  return data.titles;
}

movieInput.addEventListener("input", () => {
  const query = movieInput.value.trim();

  clearTimeout(debounceTimer);
  if (query.length < 2) {
    suggestions.innerHTML = "";
    return;
  }

  debounceTimer = setTimeout(async () => {
    const titles = await searchTitles(query);
    renderSuggestions(titles);
  }, 200);
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const movie = movieInput.value.trim();
  if (!movie) {
    showError("Please enter a movie title.");
    return;
  }

  try {
    const result = await fetchRecommendations(movie);
    showResults(result.movie, result.recommendations);
  } catch (error) {
    showError(error.message);
  }
});
