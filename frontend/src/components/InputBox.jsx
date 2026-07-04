import "./InputBox.css";

function InputBox(){

    return(

        <div className="input-area">

            <input

                type="text"

                placeholder="Tulis pertanyaan..."

            />

            <button>

                Send

            </button>

        </div>

    )

}

export default InputBox;