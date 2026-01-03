export function startDownload() {
    const currInfoSpan = document.querySelector('.curr-info') as HTMLSpanElement;
    const url = (document.getElementById('url') as HTMLInputElement).value;
    const reqMediaType = (document.getElementById('media-type') as HTMLSelectElement).value;
    const abr = (document.getElementById('abr') as HTMLSelectElement).value;
    const resolution = (document.getElementById('resolution') as HTMLSelectElement).value;
    const fps = (document.getElementById('fps') as HTMLSelectElement).value;

    const downloadBtn = document.getElementById('start-download') as HTMLButtonElement;

    if (!url) {
        alert('Please enter a YouTube URL.');
        return;
    }

    currInfoSpan.textContent = `Downloading...`;
    downloadBtn.disabled = true;

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
    } catch (err: any) {
        console.error(err);
        currInfoSpan.textContent = `Error downloading: ${err.message}`;
    } finally {
        downloadBtn.disabled = false;
    }
}