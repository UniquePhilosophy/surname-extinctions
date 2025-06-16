const svg = d3.select("#viz");
const width = window.innerWidth;
const height = window.innerHeight * 0.85;
svg.attr("width", width).attr("height", height);

const generations = 50;
const interval = 1000; // ms between frames
let generationIndex = 0;

// Define your color mapping per nationality
const nationalityColors = {
  English: "#1f77b4",
  Indian: "#ff7f0e",
  Polish: "#2ca02c",
  Russian: "#d62728",
  Arabic: "#9467bd",
  Unknown: "#7f7f7f" // fallback
};

function loadCSVData(gen) {
  const genStr = gen.toString().padStart(2, '0');
  return d3.csv(`generations/generation_${genStr}.csv`, d => ({
    surname: d.Surname,
    count: +d.Count,
    nationality: d.Nationality || "Unknown"
  }));
}

function updateBubbles(data, genNumber) {
  d3.select("#generation-label").text(`Generation ${genNumber}`);

  const maxCount = d3.max(data, d => d.count);
  const radiusScale = d3.scaleSqrt().domain([1, maxCount]).range([2, 40]);

  const simulation = d3.forceSimulation(data)
    .force("charge", d3.forceManyBody().strength(0))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide(d => radiusScale(d.count) + 1))
    .stop();

  for (let i = 0; i < 120; ++i) simulation.tick();

  const bubbles = svg.selectAll("circle").data(data, d => d.surname);

  // Exit
  bubbles.exit().remove();

  // Enter
  const enter = bubbles.enter()
    .append("circle")
    .attr("r", 0)
    .attr("cx", width / 2)
    .attr("cy", height / 2)
    .attr("fill", d => nationalityColors[d.nationality] || nationalityColors.Unknown);

  // Update + Enter
  enter.merge(bubbles)
    .transition().duration(800)
    .attr("r", d => radiusScale(d.count))
    .attr("cx", d => d.x)
    .attr("cy", d => d.y)
    .attr("fill", d => nationalityColors[d.nationality] || nationalityColors.Unknown);
}

function animateGenerations() {
  loadCSVData(generationIndex).then(data => {
    updateBubbles(data, generationIndex);
    generationIndex = (generationIndex + 1) % generations;
    setTimeout(animateGenerations, interval);
  });
}

animateGenerations();

const legend = d3.select("#legend");

Object.entries(nationalityColors).forEach(([name, color]) => {
  const item = legend.append("div").attr("class", "legend-item");
  item.append("div")
      .attr("class", "legend-swatch")
      .style("background-color", color);
  item.append("span").text(name);
});

