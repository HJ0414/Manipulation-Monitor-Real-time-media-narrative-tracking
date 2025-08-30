const url = "/api/stories";
async function load() {
  const res = await fetch(url);
  const data = await res.json();

  // group by evolution_index
  const grouped = {};
  data.forEach(a => {
    const idx = (a.evolution_index === undefined || a.evolution_index === null) ? 0 : a.evolution_index;
    const k = `${a.source}-${idx}`;
    if (!grouped[k]) grouped[k] = 0;
    grouped[k] += 1;
  });

  const labels = Object.keys(grouped);
  const values = Object.values(grouped);

  // draw / update Chart.js
  if (window.chart) {
    window.chart.data.labels = labels;
    window.chart.data.datasets[0].data = values;
    window.chart.update();
  } else {
    const ctx = document.getElementById("evoChart");
    window.chart = new Chart(ctx, {
      type: "bar",
      data: { labels, datasets: [{ label: "Story Mutations", data: values }] },
      options: { }
    });
  }
}
setInterval(load, 60000); // refresh every minute
load();
