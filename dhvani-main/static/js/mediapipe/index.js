// Copyright 2023 The MediaPipe Authors.
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//      http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
// import audio from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-audio@0.10.0";

import audio from "./audio_bundle.js";
const { AudioClassifier, AudioClassifierResult, FilesetResolver } = audio;
const demosSection = document.getElementById("demos");
let isPlaying = false;
let audioClassifier;
let audioCtx;
const createAudioClassifier = async () => {
    // const audio = await FilesetResolver.forAudioTasks("https://cdn.jsdelivr.net/npm/@mediapipe/tasks-audio@0.10.0/wasm");
    const audio = await FilesetResolver.forAudioTasks("../static/js/mediapipe/wasm");
    // const audio = await FilesetResolver.forAudioTasks({{ url_for('static'), filename='js/mediapipe/wasm'}});
    audioClassifier = await AudioClassifier.createFromOptions(audio, {
        baseOptions: {
            // modelAssetPath: "https://storage.googleapis.com/mediapipe-models/audio_classifier/yamnet/float32/1/yamnet.tflite"
            modelAssetPath: "../static/js/mediapipe/yamnet.tflite"
            // modelAssetPath: {{ url_for('static'), filename='js/mediapipe/yamnet.tflite'}}
        }
    });
    demosSection.classList.remove("invisible");
};
createAudioClassifier();
const socket = io.connect("http://127.0.0.1:5000/");
/*
  Demo 2 - Streaming classification from microphone
*/
const streamingBt = document.getElementById("microBt");
// streamingBt.addEventListener("click", async function () {
//     await runStreamingAudioClassification();
// });

setTimeout(async function () {
    await runStreamingAudioClassification();
}, 2000)

async function runStreamingAudioClassification() {
    const output = document.getElementById("microResult");
    const constraints = { audio: true };
    let stream;
    try {
        stream = await navigator.mediaDevices.getUserMedia(constraints);
    }
    catch (err) {
        console.log("The following error occured: " + err);
        alert("getUserMedia not supported on your browser");
    }
    if (!audioCtx) {
        audioCtx = new AudioContext({ sampleRate: 16000 });
    }
    else if (audioCtx.state === "running") {
        await audioCtx.suspend();
        streamingBt.firstElementChild.innerHTML = "START CLASSIFYING";
        return;
    }
    // resumes AudioContext if has been suspended
    await audioCtx.resume();
    streamingBt.firstElementChild.innerHTML = "STOP CLASSIFYING";
    const source = audioCtx.createMediaStreamSource(stream);
    const scriptNode = audioCtx.createScriptProcessor(16384, 1, 1);
    scriptNode.onaudioprocess = function (audioProcessingEvent) {
        const inputBuffer = audioProcessingEvent.inputBuffer;
        let inputData = inputBuffer.getChannelData(0);
        // Classify the audio
        const result = audioClassifier.classify(inputData);
        const categories = result[0].classifications[0].categories;
        // Display results
        output.innerText =
            categories[0].categoryName +
            "(" +
            categories[0].score.toFixed(3) +
            ")\n" +
            categories[1].categoryName +
            "(" +
            categories[1].score.toFixed(3) +
            ")\n" +
            categories[2].categoryName +
            "(" +
            categories[2].score.toFixed(3) +
            ")";
        process_classification(categories)
    };
    source.connect(scriptNode);
    scriptNode.connect(audioCtx.destination);
}

function process_classification(data){
  const result = []
  let footstep = data.filter(item => item.categoryName.toLowerCase().includes('foot'))
  if(footstep[0].score !== 0){
    map_name(footstep[0], 'Footstep')
    result.push(footstep[0])
  }
  let clap = data.filter(item => item.categoryName.toLowerCase().includes('hand') || item.categoryName.toLowerCase().includes('clap') || item.categoryName.toLowerCase().includes('applause'))
  clap = get_highest_score(clap);
  if(clap !== null){
    map_name(clap, 'Clap')
    result.push(clap)
  }
  let voice = data.filter(item => item.categoryName.toLowerCase().includes('speech'))
  voice = get_highest_score(voice);
  if(voice !== null){
    map_name(voice, 'Voice')
    result.push(voice)
  }
  let door = data.filter(item => item.categoryName.toLowerCase().includes('door'))
  door = get_highest_score(door);
  if(door !== null){
    map_name(door, 'Bell')
    result.push(door)
  }
  // console.log(result);
  const classification = get_highest_score(result)
  console.log(classification);
  if(classification.score >= 0.2){
    const obj = { "sound_type": classification.displayName, "accuracy": 99, "id": Date.now() };
    socket.send(obj)
  }
}


const sound = () => {
    const sounds = ["Clap", "Voice", "Footstep", "Bell"]
    const rand_idx = Math.floor(Math.random() * sounds.length)
    console.log(rand_idx, sounds[rand_idx]);
    return sounds[rand_idx]
}

function get_highest_score(arr) {
  const result = arr.reduce((acc, curr) => {
    return acc.score > curr.score ? acc : curr;
  });
  if(result.score == 0){
    return null
  }
  return result;
}

function map_name(obj, name){
  obj.displayName = name
}

