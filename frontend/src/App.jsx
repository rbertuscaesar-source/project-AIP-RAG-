import "./App.css";

import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import UploadBox from "./components/UploadBox";
import ChatBox from "./components/ChatBox";
import InputBox from "./components/InputBox";

function App() {

  return (

    <div className="app">

      <Header />

      <div className="content">

        <Sidebar />

        <div className="main">

          <UploadBox />

          <ChatBox />

          <InputBox />

        </div>

      </div>

    </div>

  );

}

export default App;