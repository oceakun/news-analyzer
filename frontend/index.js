document.addEventListener("DOMContentLoaded", function () {
  const getAllHighlightsUrl = "http://127.0.0.1:5000/api/news_headlines";
  const answerQueryUrl = "http://127.0.0.1:5000/api/answer_query";
  const containerListElement = document.querySelector(".container-list");
  const inputElement = document.querySelector(".input-bar");
  const searchIcon = document.querySelector(".search-icon");

  function truncateText(text, wordLimit) {
    const words = text.split(" ");
    if (words.length > wordLimit) {
      return words.slice(0, wordLimit).join(" ") + "...";
    }
    return text;
  }

  function extractCategoryFromUrl(url) {
    const baseUrl = "https://timesofindia.indiatimes.com/";
    const categoryRegex =
      /^https:\/\/timesofindia\.indiatimes\.com\/([^\/]+)\/?/;
    const match = url.match(categoryRegex);

    if (match && match[1]) {
      // The first capturing group should be the category
      return match[1];
    } else {
      return "Unknown"; // Default category if not found
    }
  }

  function keepLatestUniqueRecords(records) {
    const latestRecordsMap = new Map();
    records.forEach((record) => {
      latestRecordsMap.set(record.title, record);
    });

    return Array.from(latestRecordsMap.values());
  }

  function fetchAllNews() {
    fetch(getAllHighlightsUrl)
      .then((response) => response.json())
      .then((data) => {
        console.log("data : ", data);
        const similarNews = data.news_headlines;
        const uniqueLatestNews = keepLatestUniqueRecords(similarNews);
        console.log("uniqueLatestNews : ", uniqueLatestNews);
        uniqueLatestNews.forEach((headline) => {
          const containerElement = document.createElement("div");
          containerElement.className = "container";
          const truncatedArticle = truncateText(headline.article, 40);
          const category = extractCategoryFromUrl(headline.url);
          containerElement.setAttribute(
            "data-category",
            category.toLowerCase()
          );
          containerElement.innerHTML = `
          <h3>${headline.title}</h3>
          <p>${truncatedArticle}</p>
          <div class="footer">
            <a href="${headline.url}" target="_blank" class="url">Read more</a>
            <span class="category">${category}</span>
          </div>
        `;
          containerListElement.appendChild(containerElement);
        });
      })
      .catch((error) => {
        console.error("Error fetching news headlines:", error);
      });
  }

  function fetchSimilarNews(query) {
    fetch(answerQueryUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query: query }),
    })
      .then((response) => response.json())
      .then((data) => {
        const similarNews = data.data;
        const uniqueLatestNews = keepLatestUniqueRecords(similarNews);

        containerListElement.innerHTML = "";

        uniqueLatestNews.forEach((newsItem) => {
          const containerElement = document.createElement("div");
          containerElement.className = "container";
          containerElement.innerHTML = `
          <h3>${newsItem.title}</h3>
          <p>${truncateText(newsItem.article, 40)}</p>
          <div class="footer">
            <a href="${newsItem.url}" target="_blank" class="url">Read more</a>
            <span class="category">${newsItem.category}</span>
          </div>
        `;
          containerListElement.appendChild(containerElement);
        });
      })
      .catch((error) => console.error("Error fetching similar news:", error));
  }

  searchIcon.addEventListener("click", function () {
    const query = inputElement.value.trim();
    if (query) {
      fetchSimilarNews(query);
    } else {
      alert("Please enter a query.");
    }
  });

  fetchAllNews();

  document.querySelectorAll(".filter-btn").forEach((button) => {
    button.addEventListener("click", function () {
      const filter = this.getAttribute("data-filter"); // Get the filter from the button

      document.querySelectorAll(".container").forEach((container) => {
        // Compare the container's category to the selected filter
        if (
          filter === "all" ||
          container.getAttribute("data-category") === filter.toLowerCase()
        ) {
          container.style.display = ""; // Show the container
        } else {
          container.style.display = "none"; // Hide the container
        }
      });
    });
  });
});
