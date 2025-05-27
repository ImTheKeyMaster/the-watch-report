fetch('data/news.json')
  .then(res => res.json())
  .then(data => {
    const container = document.getElementById('news');
    container.innerHTML = '';

    if (data.length === 0) {
      container.innerHTML = '<p>No news articles found.</p>';
      return;
    }

    // Highlight main story
    const main = data[0];
    const mainArticle = document.createElement('article');
    mainArticle.innerHTML = `
      <h2><a href="${main.link}" target="_blank">${main.title}</a></h2>
      ${main.image ? `<img src="${main.image}" alt="${main.title}"/>` : ''}
      <p><a href="${main.link}" target="_blank">Read more</a></p>
    `;
    container.appendChild(mainArticle);

    // Add remaining stories
    for (let i = 1; i < data.length; i++) {
      const story = data[i];
      const article = document.createElement('article');
      article.innerHTML = `
        <h3><a href="${story.link}" target="_blank">${story.title}</a></h3>
      `;
      container.appendChild(article);
    }
  })
  .catch(err => {
    document.getElementById('news').innerHTML = '<p>Unable to load news.</p>';
    console.error(err);
  });
