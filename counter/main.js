// element refs
var timeInfo = document.getElementById('time-info');
var video = document.getElementById('video');
var videoSource = document.getElementById('video-source');
var videoFileChooser = document.getElementById('video-file');
var speedSlider = document.getElementById('playbackRate');
var speedLabel = document.getElementById('speed-label');
var logContainer = document.getElementById('log');
var processedLogContainer = document.getElementById('processed-log');

var countBtn = document.getElementById('count-btn');
var startBtn = document.getElementById('start-btn');
var pauseBtn = document.getElementById('pause-btn');
var analyzeBtn = document.getElementById('analyze-btn');
var resetBtn = document.getElementById('reset-btn');
var spoolBtn = document.getElementById('spool-btn');

// initialization
video.playbackRate = 1;
var FILENAME;
var STARTED = false;
var COUNTS = [];
var GROUP_COUNTS_BY = 5;

// event listeners
videoFileChooser.addEventListener('change', (event) => {
  FILENAME = event.target.files[0].name;
  videoSource.src = URL.createObjectURL(event.target.files[0]);
  video.load();
  timeInfo.style.display = 'none';
});

video.addEventListener('timeupdate', (event) => {
  var ct = video.currentTime;
  var ct_h = Math.floor(ct / 3600);
  var ct_m = Math.floor((ct - ct_h * 3600) / 60);
  var ct_s = Math.floor(ct - ct_m * 60 - ct_h  * 3600);
  var ct_label = `${ct_h < 10 ? '0' + ct_h : ct_h}:${ct_m < 10 ? '0' + ct_m : ct_m}:${ct_s < 10 ? '0' + ct_s : ct_s}`;

  var duration = video.duration;
  var duration_h = Math.floor(duration / 3600);
  var duration_m = Math.floor((duration - duration_h * 3600) / 60);
  var duration_s = Math.floor(duration - duration_m * 60 - duration_h  * 3600);
  var duration_label = `${duration_h < 10 ? '0' + duration_h : duration_h}:${duration_m < 10 ? '0' + duration_m : duration_m}:${duration_s < 10 ? '0' + duration_s : duration_s}`;

  timeInfo.innerText = `${ct_label} / ${duration_label} (${Math.floor(ct/duration * 100)}%)`;
});

speedSlider.addEventListener('change', (event) => {
  speedLabel.innerText = speedSlider.value + 'x';
  video.playbackRate = speedSlider.value;
});

document.body.addEventListener('keydown', (event) => {
  if (event.code == 'Space') {
    event.stopPropagation();
    event.preventDefault();

    count();
    log();
  } else if (event.code == 'ArrowRight') {
    speedSlider.value = +speedSlider.value + 0.5;
    speedSlider.dispatchEvent(new Event('change'));
  } else if (event.code == 'ArrowLeft') {
    speedSlider.value = +speedSlider.value - 0.5;
    speedSlider.dispatchEvent(new Event('change'));
  }
});

countBtn.addEventListener('click', () => {
  count();
  log();
});

startBtn.addEventListener('click', (e) => {
  start();
  e.target.disabled = true;
  countBtn.disabled = false;
  analyzeBtn.disabled = false;
  pauseBtn.disabled = false;
  timeInfo.style.display = 'block';
});

pauseBtn.addEventListener('click', (e) => {
  pause();
  e.target.disabled = true;
  countBtn.disabled = true;
  startBtn.disabled = false;
  analyzeBtn.disabled = false;
});

analyzeBtn.addEventListener('click', (e) => {
  analyze();
  e.target.disabled = true;
  countBtn.disabled = true;
  startBtn.disabled = false;
  pauseBtn.disabled = true;
});

resetBtn.addEventListener('click', (e) => {
  reset();
  countBtn.disabled = true;
  startBtn.disabled = false;
  pauseBtn.disabled = true;
  analyzeBtn.disabled = true;
});

spoolBtn.addEventListener('click', () => {
  video.currentTime = document.getElementById('secs').value || 0;
});

// functions
function reset() {
  processedLogContainer.innerHTML = '';
  logContainer.innerHTML = '';
  COUNTS = [];
  video.pause();
  video.currentTime = 0;
}

function start() {
  STARTED = true;
  video.play();
}

function pause() {
  video.pause();
  STARTED = false;
}

function analyze() {
  video.pause();
  STARTED = false;
  var now = new Date();

  if (COUNTS && COUNTS.length) {
    processedLogContainer.innerHTML = '';
    var lastItem = COUNTS[COUNTS.length - 1];
    var groupedCounts = [];
    for (let i = 0; i <= lastItem.second; i += GROUP_COUNTS_BY) {
      var filtered = COUNTS.filter(item => item.second >= i && item.second < i + GROUP_COUNTS_BY);
      var sum = 0;
      filtered.forEach(item => {
        sum += item.count;
      });
      groupedCounts.push({toSecond: i + GROUP_COUNTS_BY, sum: sum});
      processedLogContainer.innerHTML += `${i}s bis ${i + GROUP_COUNTS_BY}s: ${sum}<br>`;
    }

    // save to localStorage
    localStorage.setItem(`hsnr-traffic-analysis-${now.getTime()}`, JSON.stringify({
      dateTime: now.toLocaleString(),
      videoFileName: FILENAME,
      groupedCounts: groupedCounts,
      origCounts: COUNTS
    }));
  }
}

function count() {
  if (!STARTED) {
    return;
  }
  var currentTime = Math.floor(video.currentTime);
  var item = COUNTS.find(i => i.second == currentTime);
  if (item) {
    item.count++;
  } else {
    COUNTS.push({second: currentTime, count: 1});
  }
}

function log() {
  if (!STARTED) {
    return;
  }
  logContainer.innerHTML = '';
  COUNTS.forEach(item => {
    logContainer.innerHTML += `${item.second}s => ${item.count} Fahrzeug(e)<br>`;
  });
}