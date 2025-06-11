  <script src="{{ url_for('static', filename='js/ort.min.js') }}" defer>
  // <script>
      // window.startCamera = startCamera;
      // window.captureAndRecognize = captureAndRecognize;
      // window.saveData = saveData;
      // window.uploadData = uploadData;
      // window.initModel = initModel;
      let db;
      const request = indexedDB.open("BusinessCardDB", 1);

      request.onerror = (e) => console.error("❌ 資料庫開啟失敗", e);

      request.onsuccess = (e) => {
          db = e.target.result;
          updateCount();
      };

      request.onupgradeneeded = (e) => {
          db = e.target.result;
          db.createObjectStore("cards", { keyPath: "id", autoIncrement: true });
      };

      async function initModels() {
          yoloSession = await InferenceSession.create('/static/models/yolo_model.onnx');
          ocrSession = await InferenceSession.create('/static/models/ocr_model.onnx');
          console.log('✅ ONNX 模型載入成功');
      }

      window.captureAndRecognize = async () => {
          if (!yoloSession || !ocrSession) await initModels();

          const video = document.getElementById('video');
          const canvas = document.getElementById('canvas');
          const ctx = canvas.getContext('2d');
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

          // YOLO input resize
          const yWidth = 640, yHeight = 640;
          const yCanvas = document.createElement('canvas');
          yCanvas.width = yWidth; yCanvas.height = yHeight;
          const yCtx = yCanvas.getContext('2d');
          yCtx.drawImage(canvas, 0, 0, yWidth, yHeight);
          const yImg = yCtx.getImageData(0,0,yWidth,yHeight).data;
          const yArr = new Float32Array(yWidth * yHeight * 3);
          for (let i=0; i < yWidth*yHeight; i++){
              yArr[i*3] = yImg[i*4]/255;
              yArr[i*3+1] = yImg[i*4+1]/255;
              yArr[i*3+2] = yImg[i*4+2]/255;
          }
          const yTensor = new ort.Tensor('float32', yArr, [1,3,yHeight,yWidth]);
          const yOut = await yoloSession.run({ images: yTensor });
          const [boxes, scores, labels] = decodeYolo(yOut.output, canvas.width, canvas.height);

          if (boxes.length === 0) {
              alert('❌ 偵測不到文字框');
              return;
          }

          // 先取第一個框
          const [x, y, w, h] = boxes[0];
          const oImg = ctx.getImageData(x, y, w, h);
          const oc = document.createElement('canvas');
          oc.width = w; oc.height = h;
          oc.getContext('2d').putImageData(oImg,0,0);

          const imgArr = oc.getContext('2d').getImageData(0,0,w,h).data;
          const oArr = new Float32Array(w*h*3);
          for (let i=0; i< w*h; i++){
              oArr[i*3] = imgArr[i*4]/255;
              oArr[i*3+1] = imgArr[i*4+1]/255;
              oArr[i*3+2] = imgArr[i*4+2]/255;
          }
          const oTensor = new ort.Tensor('float32', oArr, [1,3,h,w]);
          const oOut = await ocrSession.run({ input: oTensor });
          const text = decodeOCR(oOut.output.data);
          console.log('🔤 辨識結果:', text);

          // 自動統計欄位
          const lines = text.split(/\s*[\n，。]\s*/);
          document.getElementById('System').value = lines[0] || '';
          document.getElementById('Number').value = lines[1] || '';
          document.getElementById('ocr-status').textContent = '✅ 文字辨識完成！';
      };

      function decodeYolo(output, imgW, imgH) {
          // 假設格式 output = [ [ [x, y, w, h, score, label] ] ]
          const arr = output.data;
          const out = [];
          for (let i=0; i < arr.length; i+=6) {
              const score = arr[i+4];
              if (score > 0.4) {
                  const cx=arr[i], cy=arr[i+1], w=arr[i+2], h=arr[i+3];
                  const x = (cx - w/2)*imgW;
                  const y = (cy - h/2)*imgH;
                  out.push([x,y,w*imgW,h*imgH]);
              }
          }
          return [out, [], []];
      }

      function decodeOCR(dataArr) {
          // 假設 CTC blacklist，非 blank 為文字索引
          const dict = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ中文巡檢點系統空白';
          let txt='';
          let prev = -1;
          const seqLen = dataArr.length / dict.length;
          for (let t=0; t<seqLen; t++) {
              const slice = dataArr.slice(t*dict.length, (t+1)*dict.length);
              const idx = slice.indexOf(Math.max(...slice));
              if (idx > 0 && idx !== prev) txt += dict[idx];
              prev = idx;
          }
          return txt;
      }
    // =================================================================================================================

      function saveData() {
          const System = document.getElementById("System").value.trim();

          const Number = document.getElementById("Number").value.trim();

          if (!System || !Number) {
              alert("請完整輸入所有欄位！");
              return;
          }

          const tx = db.transaction("cards", "readwrite");
          const store = tx.objectStore("cards");
          store.add({ System, Number });
          tx.oncomplete = () => {
              document.getElementById("System").value = '';
              document.getElementById("Number").value = '';
              updateCount();
              alert("✅ 已儲存至本地");
          };
      }

      function updateCount() {
          const tx = db.transaction("cards", "readonly");
          const store = tx.objectStore("cards");
          const countReq = store.count();
          countReq.onsuccess = () => {
              document.getElementById("status").textContent = `📦 本地暫存筆數：${countReq.result}`;
          };
      }

      function uploadData() {
          const tx = db.transaction("cards", "readonly");
          const store = tx.objectStore("cards");
          const getAll = store.getAll();

          getAll.onsuccess = () => {
              const data = getAll.result;
              if (data.length === 0) {
                  alert("⚠️ 沒有可上傳的資料！");
                  return;
              }

              fetch("/upload", {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify(data),
              })
                  .then(res => res.json())
                  .then(res => {
                      if (res.success) {
                          const clearTx = db.transaction("cards", "readwrite");
                          clearTx.objectStore("cards").clear();
                          updateCount();
                          alert("✅ 上傳成功，已清除本地資料");
                      } else {
                          alert("❌ 上傳失敗");
                      }
                  });
          };
      }

      // ========= 鏡頭拍照與 OCR 功能 =========

      let stream;

      async function startCamera() {
          try {
              stream = await navigator.mediaDevices.getUserMedia({ video: true });
              document.getElementById("video").srcObject = stream;
          } catch (err) {
              alert("無法啟用鏡頭：" + err.message);
          }
      }

      function captureAndRecognize() {
          const video = document.getElementById("video");
          const canvas = document.getElementById("canvas");
          const ctx = canvas.getContext("2d");

          // 動態設解析度
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;

          // 拍照
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

          // 定義裁切區域
          const systemBox = { x: 50, y: 30, width: 400, height: 50 };
          const numberBox = { x: 50, y: 90, width: 400, height: 50 };

          // 建立子 Canvas 進行裁切
          function cropAndOCR(box, callback) {
              const subCanvas = document.createElement("canvas");
              subCanvas.width = box.width;
              subCanvas.height = box.height;
              const subCtx = subCanvas.getContext("2d");
              subCtx.drawImage(canvas, box.x, box.y, box.width, box.height, 0, 0, box.width, box.height);
              const dataURL = subCanvas.toDataURL("image/png");

              Tesseract.recognize(dataURL, 'chi_tra+eng', {
                  logger: m => console.log(m)
              }).then(({ data: { text } }) => {
                  callback(text.trim());
              }).catch(err => {
                  console.error("OCR 錯誤：", err);
                  callback("");
              });
          }

          document.getElementById("ocr-status").textContent = "🔍 正在辨識兩個欄位...";

          // 同步辨識兩個欄位
          cropAndOCR(systemBox, (systemText) => {
              cropAndOCR(numberBox, (numberText) => {
                  console.log("System：", systemText);
                  console.log("Number：", numberText);

                  // 設定到欄位
                  document.getElementById("System").value = systemText;
                  document.getElementById("Number").value = numberText;

                  document.getElementById("ocr-status").textContent = "✅ 已辨識並填入欄位";

                  if (!systemText || !numberText) {
                      alert("⚠️ 有欄位未能辨識成功，請確認影像清晰度或手動填入");
                  }
              });
          });
      }
      // ===============================================================================================================


  </script>