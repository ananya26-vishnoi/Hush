// Calling backend with email and creating index, next getting chatlist chatlist 
const BASE_URL = "http://127.0.0.1:8000"
email = document.getElementById("email").value;
var indexData = new FormData();
indexData.append("email", email);

indexData.append("csrfmiddlewaretoken", document.getElementsByName('csrfmiddlewaretoken')[0].value);
$.ajax({
    url: BASE_URL + "/createIndex",
    type: "POST",
    data: indexData,
    processData: false,
    contentType: false,
    success: function (response) {
        // Index has been created now lets get chatlist
        var chat_list_url = BASE_URL + "/getChatList?email=" + email;
        $.ajax({
            url: chat_list_url,
            type: "GET",
            success: function (response) {
                // Chat list has been received
                chat_data = response["data"]
                make_chat_list(chat_data)
            },
            error: function (error) {
                console.log(error);
            }
        });
        // stop loader
        document.getElementById('loading').style.display = "none";
        // show toast
        document.getElementById("desc_correct").innerHTML = "All Documents Fetched";
        launch_toast_correct();
    },
    error: function (error) {
        console.log(error);
        // stop loader
        document.getElementById('loading').style.display = "none";
        //show error toast
        document.getElementById("desc_correct").innerHTML = "Error! Please login again";
        launch_toast();
    }
});

// If enter is pressed in message input tab then this is used to handle that
const myInput = document.getElementById("message_send");
myInput.addEventListener("keydown", function (event) {
    if (event.keyCode === 13) {
        message_handler();
        event.preventDefault();
    }
});

// Setting username
document.getElementById("name").innerHTML = document.getElementById("shortname").value;

// This is used to create a user message
function append_user_message(message) {
    var message_div = document.createElement("div");
    message_div.className = "user_message";
    var name_dev = document.createElement("div");
    name_dev.className = "name_user_img";
    name_dev.innerHTML = document.getElementById("shortname").value;
    var message_Div = document.createElement("p");
    message_Div.innerHTML = message;
    message_div.appendChild(name_dev);
    message_div.appendChild(message_Div);
    var outer_div = document.getElementById("message_field_inner");
    outer_div.appendChild(message_div);
}

// This is used to create a message by bot
function append_bot_message(message) {
    var message_div = document.createElement("div");
    message_div.className = "bot_message";
    var name_dev = document.createElement("img");
    name_dev.src = "/static/images/bot_message.png";
    var message_Div = document.createElement("p");
    message_Div.innerHTML = message;
    message_div.appendChild(name_dev);
    message_div.appendChild(message_Div);
    var outer_div = document.getElementById("message_field_inner");
    outer_div.appendChild(message_div);
}

// This is a message handler that gets message from user and then calls bot and then prints its message too
function message_handler() {
    var message = document.getElementById("message_send").value;
    document.getElementById("message_send").value = "";
    if (message != "") {
        append_user_message(message);
        chat(message);
    }
}



// Create chat list
function make_chat_list(chat_data) {
    document.getElementById('chat_list_data').value = JSON.stringify(chat_data);
    // Traversing data and making divs
    for (var i = 0; i < chat_data.length; i++) {
        var folder_file_div = document.createElement("div");
        folder_file_div.className = "folder_file";
        folder_file_div.id = chat_data[i]["index_id"];
        var img = document.createElement("img");
        if (chat_data[i]["chat_type"] == "folder") {
            img.src = "/static/images/folder.png"
        }
        else {
            img.src = "/static/images/file.png"
        }
        var folder_file_name = document.createElement("div");
        folder_file_name.className = "folder_file_name";
        folder_file_name.innerHTML = chat_data[i]["name"];
        var time_of_upload = document.createElement("div");
        time_of_upload.className = "time_of_upload";
        time_of_upload.innerHTML = chat_data[i]["timestamp"]
        folder_file_div.appendChild(img)
        folder_file_div.appendChild(folder_file_name)
        folder_file_div.appendChild(time_of_upload)
        folder_file_div.addEventListener('click', (function (chatId) {
            return function () {
                openChat(chatId);
            };
        })(chat_data[i]["index_id"]));
        document.getElementById("all_folders_and_files").appendChild(folder_file_div)
        
    }

}

// Open a particular chat
function openChat(chat_id) {
    // getting chat history
    $.ajax({
        url: BASE_URL + "/chatHistory?email=" + email + "&index_id=" + chat_id,
        type: "GET",
        success: function (response) {
            // Chat list has been received
            chat_history_data = response["data"]
            // Calling make_history function
            make_chat_history(chat_history_data, chat_id)
        },
        error: function (error) {
            console.log(error);
        }
    });

    document.getElementById("chat_heading").style.display = "flex"
    var json_chat_list_data = document.getElementById("chat_list_data").value;
    json_chat_list_data = JSON.parse(json_chat_list_data);
    chat_data = ""
    for (var i = 0; i < json_chat_list_data.length; i++) {
        if (json_chat_list_data[i]["index_id"] == chat_id) {
            chat_data = json_chat_list_data[i]
            break
        }
    }

    // now we have chat_data
    document.getElementById("chat_heading_name").innerHTML = chat_data["name"]
    document.getElementById("message_field_inner").innerHTML = ""

    // remove active_link from all other divs under the di with id all_folders_and_files
    var all_folders_and_files = document.getElementById("all_folders_and_files").children;
    for (var i = 0; i < all_folders_and_files.length; i++) {
        if (all_folders_and_files[i].id != chat_id) {
            all_folders_and_files[i].classList.remove("active_file")
        }
    }
    document.getElementById("active_chat").value = chat_id;
    document.getElementById(chat_id).classList.add("active_file")
    document.getElementById("message_send_outer").style.display = "block"


}

// Create messages in chat history 
function make_chat_history(chat_history_data, chat_id) {
    for (var i = 0; i < chat_history_data.length; i++) {
        user_question = chat_history_data[i]["question"]
        bot_answer = chat_history_data[i]["answer"]
        append_user_message(user_question)
        append_bot_message(bot_answer)
    }
}

// to open chat settings modal
function opensettings() {
    document.getElementById("chat_settings").style.display = "flex"
    var chat_name = document.getElementById("chat_heading_name").innerHTML;
    var chat_id = document.getElementById("active_chat").value;
    document.getElementById("chat_settings_name").innerHTML = chat_name;
    var chat_data = document.getElementById("chat_list_data").value;
    var files = []
    var total_file = 0
    chat_data = JSON.parse(chat_data);
    for (var i = 0; i < chat_data.length; i++) {
        if (chat_data[i]["index_id"] == chat_id) {
            files = chat_data[i]["all_files"]
            total_file = files.length
            break
        }
    }

    document.getElementById("filelist_names").innerHTML = ""
    document.getElementById("filecount").innerHTML = total_file + " Files";
    for (var i = 0; i < files.length; i++) {
        var file_div = document.createElement("div");
        var img = document.createElement("img");
        img.src = "/static/images/file.png"
        var file_name = document.createElement("p");
        file_name.innerHTML = files[i];
        file_div.appendChild(img)
        file_div.appendChild(file_name)
        document.getElementById("filelist_names").appendChild(file_div)
    }
}

// To close chat settings modal
function closesettings() {
    document.getElementById("chat_settings").style.display = "none"
}


// Start new chat modal
var modal = document.getElementById("myModal");

// Get the button that opens the modal

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks the button, open the modal 
function open_new_doc_modal() {
    modal.style.display = "block";
    document.getElementById("upload_folder_div").style.display = "none";
    document.getElementById("upload_folder").style.display = "none";
    document.getElementById("upload_document").style.display = "none";
    document.getElementById("options_for_upload").style.display = "block";
    document.getElementById("upload_files_div").style.display = "none";
    document.getElementById("show_next_div").style.display = "block";
}
// When the user clicks on <span> (x), close the modal
span.onclick = function () {
    modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
function set_upload_type(type) {
    document.getElementById("upload_type").value = type;
}

function show_next() {
    var type = document.getElementById("upload_type").value;
    if (type == "folder") {
        document.getElementById("upload_folder_div").style.display = "block";
        document.getElementById("upload_folder").style.display = "block";
        document.getElementById("upload_document").style.display = "none";
        document.getElementById("options_for_upload").style.display = "none";
        document.getElementById("upload_files_div").style.display = "none";
        document.getElementById("show_next_div").style.display = "none";
    }
    else{
        document.getElementById("upload_folder_div").style.display = "none";
        document.getElementById("upload_folder").style.display = "none";
        document.getElementById("upload_document").style.display = "block";
        document.getElementById("options_for_upload").style.display = "none";
        document.getElementById("upload_files_div").style.display = "block";
        document.getElementById("show_next_div").style.display = "none";
    }
    
}


// User modal
// Start new chat modal
var usermodal = document.getElementById("userModal");

// Get the button that opens the modal


// When the user clicks the button, open the modal 
function open_user_modal() {
    usermodal.style.display = "block";
}


// When the user clicks anywhere outside of the modal, close it
window.onclick = function (event) {
    if (event.target == modal || event.target == usermodal) {
        modal.style.display = "none";
        usermodal.style.display = "none";
    }
}

function add_to_chatList(index_id, chat_type, timestamp, name, all_files) {
    var folder_file_div = document.createElement("div");
    folder_file_div.className = "folder_file";
    folder_file_div.id = index_id;
    var img = document.createElement("img");
    if (chat_type == "folder") {
        img.src = "/static/images/folder.png"
    }
    else {
        img.src = "/static/images/file.png"
    }
    var folder_file_name = document.createElement("div");
    folder_file_name.className = "folder_file_name";
    folder_file_name.innerHTML = name;
    var time_of_upload = document.createElement("div");
    time_of_upload.className = "time_of_upload";
    time_of_upload.innerHTML = timestamp
    folder_file_div.appendChild(img)
    folder_file_div.appendChild(folder_file_name)
    folder_file_div.appendChild(time_of_upload)
    folder_file_div.addEventListener('click', (function (chatId) {
        return function () {
            openChat(chatId);
        };
    })(index_id));
    document.getElementById("all_folders_and_files").appendChild(folder_file_div)
    var chat_data = document.getElementById("chat_list_data").value;
    chat_data = JSON.parse(chat_data);
    chat_data.push({ "index_id": index_id, "chat_type": chat_type, "timestamp": timestamp, "name": name, "all_files": all_files })
    document.getElementById("chat_list_data").value = JSON.stringify(chat_data);

}

function upload_files() {
    document.getElementById('loading').style.display = "block";
    var file = document.getElementById("file").files[0];
    var formData = new FormData();
    formData.append("file", file);
    email = document.getElementById("email").value;
    formData.append("email", email);
    formData.append("csrfmiddlewaretoken", document.getElementsByName('csrfmiddlewaretoken')[0].value);
    $.ajax({
        url: BASE_URL + "/uploadFile",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            document.getElementById("myModal").style.display = 'none';
            var index_id = response["index_id"];
            add_to_chatList(index_id, "file", "1s", file.name, []);

            // stop loader
            document.getElementById('loading').style.display = "none";
            // show toast
            document.getElementById("desc_correct").innerHTML = "File Uploaded Successfully";
            launch_toast_correct();
        },
        error: function (error) {
            console.log(error);
            // stop loader
            document.getElementById('loading').style.display = "none";
            //show error toast
            document.getElementById("desc_correct").innerHTML = "Error Uploading File";
            launch_toast();
        }
    });
}

function upload_folder() {
    document.getElementById('loading').style.display = "block";
    var file = document.getElementById("folder").files;
    var relativePath = file[0].webkitRelativePath;
    var folder = relativePath.split("/");
    folder = folder[0]
    var all_files = []
    var total_files = file.length;

    var formData = new FormData();
    for (var i = 0; i < total_files; i++) {
        folder_name = "folder_" + i;
        all_files.push(file[i].name)
        formData.append(folder_name, file[i]);
    }
    email = document.getElementById("email").value;
    formData.append("total_files", total_files);
    formData.append("email", email);
    formData.append("folder_name", folder);
    formData.append("csrfmiddlewaretoken", document.getElementsByName('csrfmiddlewaretoken')[0].value);
    $.ajax({
        url: BASE_URL + "/uploadFolder",
        type: "POST",
        data: formData, // Use the FormData directly here
        processData: false,
        contentType: false, // Set contentType to false when using FormData
        success: function (response) {
            document.getElementById("myModal").style.display = 'none';
            var index_id = response["index_id"];

            add_to_chatList(index_id, "folder", "1s", folder, all_files);

            // stop loader
            document.getElementById('loading').style.display = "none";
            // show toast
            document.getElementById("desc_correct").innerHTML = "Folder Uploaded Successfully";
            launch_toast_correct();
        },
        error: function (error) {
            console.log(error);
            // stop loader
            document.getElementById('loading').style.display = "none";
            //show error toast
            document.getElementById("desc_correct").innerHTML = "Error Uploading Folder";
            launch_toast();
        }
    });
}

function clear_conversation() {
    var index_id = document.getElementById("active_chat").value;
    var formData = new FormData();
    formData.append("index_id", index_id);
    email = document.getElementById("email").value;
    formData.append("email", email);
    $.ajax({
        url: BASE_URL + "/clearConversation",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            // Clean from frontend too
            document.getElementById("message_field_inner").innerHTML = ""
            document.getElementById("desc_correct").innerHTML = "All Chats Cleared Successfully";
            launch_toast_correct();
            
        },
        error: function (error) {
            console.log(error);
            //show error toast
            document.getElementById("desc_correct").innerHTML = "Error Clearing Chats";
            launch_toast();
        }
    });

}

function chat(message) {
    var index_id = document.getElementById("active_chat").value;
    var email = document.getElementById("email").value;
    var url = BASE_URL + "/chat?question="+message + "&email=" + email + "&index_id=" + index_id
    $.ajax({
        url: url,
        type: "GET",
        data: {},
        success: function (response) {
            append_bot_message(response["response"])
        },
        error: function (error) {
            console.log(error)
            append_bot_message("Sorry I did not understand you")
        }
    });
}

function launch_toast() {
    var x = document.getElementById("toast")
    x.className = "show";
    setTimeout(function () { x.className = x.className.replace("show", ""); }, 5000);
}
function launch_toast_correct() {
    var x = document.getElementById("toast_correct")
    x.className = "show";
    setTimeout(function () { x.className = x.className.replace("show", ""); }, 5000);
}

function openNav() {
  document.getElementById("mySidenav").style.width = "250px";
}

function closeNav() {
  document.getElementById("mySidenav").style.width = "0";
}