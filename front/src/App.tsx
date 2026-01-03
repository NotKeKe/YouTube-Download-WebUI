import './App.css'
import { startDownload } from './utils/download_btn'
import { userMediaTypeListener } from './hooks/userMediaTypeListener'

function App() {
    userMediaTypeListener()

    return (
        <>
            <header>
                <a href="/" className="logo" target="_blank"><img src="/icon.png" alt="Icon" />Downloader</a>

                <nav>
                    <a href="/" target="_blank">Home</a>
                    <a href="/docs" target="_blank">Docs</a>
                </nav>

                <a href="https://www.wales.com.tw" target="_blank">My Website</a>
            </header>

            <div className="container">
                <h1>Downloader</h1>

                <div className="form-group">
                    <label htmlFor="url">YouTube URL</label>
                    <input type="text" id="url" name="url" placeholder="Enter your YouTube URL" />
                </div>

                <div className="form-group">
                    <label htmlFor="media-type">Download Type</label>
                    <select id="media-type" name="media-type">
                        <option value="video+audio">Video + Audio</option>
                        <option value="video">Video</option>
                        <option value="audio">Audio</option>
                    </select>
                </div>

                <div className="options">
                    <div className="abr form-group">
                        <label htmlFor="abr">Audio Bitrate</label>
                        <select name="abr" id="abr">
                            <option value="-1">Best</option>
                        </select>
                    </div>

                    <div className="resolution form-group">
                        <label htmlFor="resolution">Resolution</label>
                        <select name="resolution" id="resolution">
                            <option value="-1">Best</option>
                        </select>
                    </div>

                    <div className="fps form-group">
                        <label htmlFor="fps">FPS</label>
                        <select name="fps" id="fps">
                            <option value="-1">Best</option>
                        </select>
                    </div>
                </div>

                <div className="extra-options">
                    <span>Extra Options</span>
                    <label className="checkbox-group">
                        <input type="checkbox" id="download-to-server" name="download-to-server" />
                        <span>Download to Server</span>
                    </label>
                </div>

                <button id="start-download" onClick={startDownload} className="btn">Start Download</button>
                <span className="curr-info">Hello World</span>
            </div>
        </>
    )
}

export default App
