document.addEventListener("DOMContentLoaded", function () {
    const input = document.querySelector("#id_face_image");
    const preview = document.querySelector("#face-preview");

    if (input) {
        input.addEventListener("change", function () {
            const file = input.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    preview.src = e.target.result;
                    preview.style.display = "block";
                };
                reader.readAsDataURL(file);
            } else {
                preview.style.display = "none";
                preview.src = "";
            }
        });
    }
});
