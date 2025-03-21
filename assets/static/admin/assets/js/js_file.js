<section class="section dashboard">
<h2 class="mx-2 mb-3 text-center">Take Attendance</h2>
<canvas id="photo" style="display: none;" name="capturedPhoto"></canvas>
<img id="photo-preview" src="" alt="Student Preview" style="display: none" class="col-6 my-3 mx-auto">
<div class="text-center mb-3">
<button id="openCameraBtn" class="btn btn-lg btn-primary">Open Camera</button>
</div>
<div class="text-center mb-3" id="btns" style="display: none;">
<form id="yourFormId" method="post" action="{% url 'take_attendance' %}" enctype="multipart/form-data">
{% csrf_token %}
<input type="file" id="imageFileNameInput" name="image" accept="image/*" style="display: none">
<button class="btn btn-md btn-success mx-4" type="submit">Submit</button>
</form>
<button class="btn btn-md btn-danger" id="retakeBtn">Retake</button>
</div>
<video id="camera" style="display: none; height: 300px;" autoplay class="mx-auto"></video>
<button id="captureBtn" style="display: none; max-width: 100%; height: auto;" class="btn btn-danger mx-auto m-4">Capture</button>
</section>

<div id="options">
<ul class="list-unstyled m-5" style="font-size: 15px; color: rgb(88, 82, 82); list-style-type: disc" id="uliteams">
<li class="mb-3">
<i class="bi bi-check-circle text-success me-2"></i> Rule 1: Provide a clear close-up image of students.
</li>
<li class="mb-3">
<i class="bi bi-check-circle text-success me-2"></i> Rule 2: Ensure good lighting for accurate facial recognition.
</li>
<li class="mb-3">
<i class="bi bi-check-circle text-success me-2"></i> Rule 3: Capture the entire face without obstructions.
</li>
<li class="mb-3">
<i class="bi bi-check-circle text-success me-2"></i> Rule 4: Do not submit blurry or distorted images.
</li>
<li class="mb-3">
<i class="bi bi-check-circle text-success me-2"></i> Rule 5: Follow privacy and data protection guidelines.
</li>
</ul>
</div>
<script>
var openCameraBtn = document.getElementById('openCameraBtn');
var captureBtn = document.getElementById('captureBtn');
var camera = document.getElementById('camera');
var uli = document.getElementById('uliteams');
var btns = document.getElementById('btns');
var retakeBtn = document.getElementById('retakeBtn');
var imageFileNameInput = document.getElementById('imageFileNameInput');
var photoPreview = document.getElementById('photo-preview');
var canvas = document.getElementById('photo');
var context = canvas.getContext('2d');

var imageDataURL = null; // Store image data URL

openCameraBtn.addEventListener('click', function () {
    // Access the device camera
    navigator.mediaDevices.getUserMedia({ video: true })
    .then(function (stream) {
        camera.srcObject = stream;
        camera.style.display = 'block';
        uli.style.display = 'none';
        openCameraBtn.style.display = 'none'; 
        captureBtn.style.display = 'block';
    })
    .catch(function (err) {
        console.error('Error accessing the camera: ' + err);
    });
});

captureBtn.addEventListener('click', function () {
    canvas.width = camera.videoWidth;
    canvas.height = camera.videoHeight;
    context.drawImage(camera, 0, 0, canvas.width, canvas.height);
    photoPreview.src = canvas.toDataURL('image/jpeg');
    photoPreview.style.display = 'block';
    captureBtn.style.display = 'none';
    btns.style.display = 'block';
    camera.style.display = 'none';
    
    
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === name + '=') {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    
    
    // Create a Blob from the image data
    canvas.toBlob(function (blob) {
        var formData = new FormData();
        formData.append('image', blob, 'captured_image.jpg');
        
        // Send the image data to the server using fetch
        fetch("{% url 'take_attendance' %}", {
            method: "POST",
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'), // Replace with the name of your CSRF token cookie
            }
        })
        .then((response) => {
            if (response.ok) {
                return response.json();
            }
            throw new Error("Network response was not ok.");
        })
        .then((data) => {
            console.log(data); // Handle the response from the server as needed
        })
        .catch((error) => {
            console.error("Fetch error:", error);
        });
    }, 'image/jpeg');
});

yourFormId.addEventListener('submit', function (e) {
    e.preventDefault(); 
});

retakeBtn.addEventListener('click', function () {
    photoPreview.style.display = 'none';
    btns.style.display = 'none';
    captureBtn.style.display = 'block';
    camera.style.display = 'block';
    imageFileNameInput.style.display = 'none';
    imageFileNameInput.value = ''; // Clear the input field
    
    
});

yourFormId.addEventListener('submit', function (e) {
    if (imageFileNameInput.files.length === 0) {
        e.preventDefault(); 
    }
});


</script>