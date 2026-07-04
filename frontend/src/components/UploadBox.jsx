import { useState } from "react";
import "./UploadBox.css";
import api from "../services/api";

function UploadBox() {

    const [file, setFile] = useState(null);

    const handleUpload = async () => {

        if (!file) {
            alert("Pilih file terlebih dahulu.");
            return;
        }

        const formData = new FormData();

        formData.append("file", file);

        try {

            const response = await api.post(
                "/upload",
                formData,
                {
                    headers: {
                        "Content-Type": "multipart/form-data"
                    }
                }
            );

            alert(response.data.status);

        } catch (error) {

            console.error(error);

            alert("Upload gagal.");

        }

    };

    return (

        <div className="upload">

            <input
                type="file"
                onChange={(e) => setFile(e.target.files[0])}
            />

            <button onClick={handleUpload}>

                Upload

            </button>

        </div>

    );

}

export default UploadBox;