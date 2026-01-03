const currInfoSpan = document.querySelector('.curr-info')
const cachedData = {}

document.getElementById('media-type').addEventListener('change', async(event) => {
    const reqMediaType = document.getElementById('media-type').value
    const url = document.getElementById('url').value
    const abrDiv = document.querySelector('.abr')
    const resolutionDiv = document.querySelector('.resolution')
    const fpsDiv = document.querySelector('.fps')
    const abrSelect = document.getElementById('abr')
    const resolutionSelect = document.getElementById('resolution')
    const fpsSelect = document.getElementById('fps')

    // 清除 option
    abrSelect.innerHTML = `<option value="-1">Best</option>`
    resolutionSelect.innerHTML = `<option value="-1">Best</option>`
    fpsSelect.innerHTML = `<option value="-1">Best</option>`

    if (reqMediaType === 'video+audio') {
        abrDiv.classList.remove('hidden')
        resolutionDiv.classList.remove('hidden')
        fpsDiv.classList.remove('hidden')
    } else if (reqMediaType === 'video') {
        abrDiv.classList.add('hidden')
        resolutionDiv.classList.remove('hidden')
        fpsDiv.classList.remove('hidden')
    } else if (reqMediaType === 'audio') {
        abrDiv.classList.remove('hidden')
        resolutionDiv.classList.add('hidden')
        fpsDiv.classList.add('hidden')
    }

    if (!url) return;

    currInfoSpan.textContent = `Fetching quality info...`

    let resolution, abr, fps;

    // 如果 cache 沒有資料，就去 fetch
    if (cachedData[url] === undefined) {
        try {
            const resp = await fetch('/quality', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url })
            });

            if (!resp.ok) {
                currInfoSpan.textContent = `Did you type the URL correctly? Server returned: ${resp.status}`;
                throw new Error('Network response was not ok');
            }

            const data = await resp.json();

            const title = data.title; // str
            const thumbnail_url = data.thumbnail_url; // str
            const duration = data.duration; // int
            abr = data.abr; // list[int]
            resolution = data.resolution; // list[int]
            fps = data.fps; // list[int]

            // 加到 cache
            cachedData[url] = {
                title,
                thumbnail_url,
                duration,
                abr,
                resolution,
                fps
            };
        } catch (err) {
            console.error("Fetch error:", err);
            currInfoSpan.textContent = `Did you type the URL correctly? Server returned: ${resp.status}`;
            return;
        }
    } else {
        // 從 cache 取資料
        const data = cachedData[url];
        abr = data.abr;
        resolution = data.resolution;
        fps = data.fps;
    }

    // add to options
    if (reqMediaType === 'video+audio') {
        resolution.forEach(element => {
            resolutionSelect.innerHTML += `<option value="${element}">${element}</option>`
        });
        abr.forEach(element => {
            abrSelect.innerHTML += `<option value="${element}">${element}</option>`
        });
        fps.forEach(element => {
            fpsSelect.innerHTML += `<option value="${element}">${element}</option>`
        });
    } else if (reqMediaType === 'video') {
        resolution.forEach(element => {
            resolutionSelect.innerHTML += `<option value="${element}">${element}</option>`
        });
        fps.forEach(element => {
            fpsSelect.innerHTML += `<option value="${element}">${element}</option>`
        });
    } else if (reqMediaType === 'audio') {
        abr.forEach(element => {
            abrSelect.innerHTML += `<option value="${element}">${element}</option>`
        });
    }

})

function startDownload() {
    const url = document.getElementById('url').value
    const reqMediaType = document.getElementById('media-type').value
    const abr = document.getElementById('abr').value
    const resolution = document.getElementById('resolution').value
    const fps = document.getElementById('fps').value

    const downloadBtn = document.getElementById('start-download')

    if (!url) {
        alert('Please enter a YouTube URL.')
        return
    }

    currInfoSpan.textContent = `Downloading...`
    downloadBtn.disabled = true

    try {
        fetch('/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    url: url,
                    type: reqMediaType,
                    abr: abr,
                    resolution: resolution,
                    fps: fps
                })
            })
            .then(resp => {
                if (!resp.ok) {
                    currInfoSpan.textContent = `Did you type the URL correctly? Server returned: ${resp.status}`;
                    throw new Error('Network response was not ok');
                }

                const disposition = resp.headers.get("Content-Disposition");
                let filename = "downloaded_file";

                if (disposition) {
                    // 嘗試解析 filename*=utf-8''xxx
                    const match = disposition.match(/filename\*=utf-8''(.+)/);
                    if (match && match[1]) {
                        filename = decodeURIComponent(match[1]); // 轉回中文
                    } else {
                        // 備用：解析 filename="xxx"
                        const match2 = disposition.match(/filename="(.+)"/);
                        if (match2 && match2[1]) {
                            filename = match2[1];
                        }
                    }
                }

                return resp.blob().then(blob => ({ blob, filename }));
            })
            .then(({ blob, filename }) => {
                const downloadUrl = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = downloadUrl;
                a.download = filename; // 使用解析後的檔名
                document.body.appendChild(a);
                a.click();
                a.remove();
                URL.revokeObjectURL(downloadUrl);
                currInfoSpan.textContent = `Yeahhhh we got a ${reqMediaType}!!`;
            });
    } catch (err) {
        console.error(err);
        currInfoSpan.textContent = `Error downloading: ${err.message}`;
    } finally {
        downloadBtn.disabled = false
    }
}

function capitalizeFirst(str) {
    // 讓第一個字大寫
    str = String(str || "");
    if (!str) return "";
    return str.charAt(0).toUpperCase() + str.slice(1);
}