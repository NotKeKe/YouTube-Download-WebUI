import { useEffect } from "react";

interface CachedData {
    [url: string]: {
        title: string;
        thumbnail_url: string;
        duration: number;
        abr: number[];
        resolution: number[];
        fps: number[];
    };
}
const cachedData: CachedData = {};

export function userMediaTypeListener() {
    useEffect(() => {
        const mediaTypeSelect = document.getElementById("media-type") as HTMLSelectElement | null;
        if (!mediaTypeSelect) return;

        const handler = async () => {
            const reqMediaType = (document.getElementById('media-type') as HTMLSelectElement).value;
            const currInfoSpan = document.querySelector('.curr-info') as HTMLSpanElement;
            const url = (document.getElementById('url') as HTMLInputElement).value;
            const abrDiv = document.querySelector('.abr') as HTMLDivElement;
            const resolutionDiv = document.querySelector('.resolution') as HTMLDivElement;
            const fpsDiv = document.querySelector('.fps') as HTMLDivElement;
            const abrSelect = document.getElementById('abr') as HTMLSelectElement;
            const resolutionSelect = document.getElementById('resolution') as HTMLSelectElement;
            const fpsSelect = document.getElementById('fps') as HTMLSelectElement;

            // 清除 option
            abrSelect.innerHTML = `<option value="-1">Best</option>`;
            resolutionSelect.innerHTML = `<option value="-1">Best</option>`;
            fpsSelect.innerHTML = `<option value="-1">Best</option>`;

            if (reqMediaType === 'video+audio') {
                abrDiv.classList.remove('hidden');
                resolutionDiv.classList.remove('hidden');
                fpsDiv.classList.remove('hidden');
            } else if (reqMediaType === 'video') {
                abrDiv.classList.add('hidden');
                resolutionDiv.classList.remove('hidden');
                fpsDiv.classList.remove('hidden');
            } else if (reqMediaType === 'audio') {
                abrDiv.classList.remove('hidden');
                resolutionDiv.classList.add('hidden');
                fpsDiv.classList.add('hidden');
            }

            if (!url) return;

            currInfoSpan.textContent = `Fetching quality info...`;

            let resolution: number[] = [];
            let abr: number[] = [];
            let fps: number[] = [];

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

                    const data = await resp.json() as {
                        title: string;
                        thumbnail_url: string;
                        duration: number;
                        abr: number[];
                        resolution: number[];
                        fps: number[];
                    };

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
                    currInfoSpan.textContent = `Did you type the URL correctly?`;
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
                    resolutionSelect.innerHTML += `<option value="${element}">${element}</option>`;
                });
                abr.forEach(element => {
                    abrSelect.innerHTML += `<option value="${element}">${element}</option>`;
                });
                fps.forEach(element => {
                    fpsSelect.innerHTML += `<option value="${element}">${element}</option>`;
                });
            } else if (reqMediaType === 'video') {
                resolution.forEach(element => {
                    resolutionSelect.innerHTML += `<option value="${element}">${element}</option>`;
                });
                fps.forEach(element => {
                    fpsSelect.innerHTML += `<option value="${element}">${element}</option>`;
                });
            } else if (reqMediaType === 'audio') {
                abr.forEach(element => {
                    abrSelect.innerHTML += `<option value="${element}">${element}</option>`;
                });
            }

            currInfoSpan.textContent = `Fetched quality info`;
        }

        mediaTypeSelect.addEventListener('change', handler);

        return () => {
            mediaTypeSelect.removeEventListener('change', handler)
        }
    }, []);
}