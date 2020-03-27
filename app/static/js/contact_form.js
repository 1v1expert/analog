$(document).ready(function () {
    var form = $("#feedback_form");
    var url = form.attr('action');
    form.submit(function (e) {
        e.preventDefault();
        var name = $("#id_name");
        var email = $("#id_email");
        var mobile = $("#id_phone");
        var msg = $("#id_text");
        var flag = false;
        if (name.val() == "") {
            name.closest(".form-group").addClass("has-error");
            name.focus();
            flag = false;
            return false;
        } else {
            name.closest(".form-group").removeClass("has-error").addClass("has-success");
        }
        if (email.val() == "") {
            email.closest(".form-group").addClass("has-error");
            email.focus();
            flag = false;
            return false;
        } else {
            email.closest(".form-group").removeClass("has-error").addClass("has-success");
        }
        if (msg.val() == "") {
            msg.closest(".form-group").addClass("has-error");
            msg.focus();
            flag = false;
            return false;
        } else {
            msg.closest(".form-group").removeClass("has-error").addClass("has-success");
            flag = true;
            $('input[type="submit"]').attr('disabled', 'disabled');
        }
        // var dataString = "name=" + name.val() + "&email=" + email.val() + "&mobile=" + mobile.val() + "&msg=" + msg.val();
        $(".loading").fadeIn("slow").html("Loading...");
        $.ajax({
            type: "POST", data: form.serialize(), url: url, cache: false, success: function (d) {
                $(".form-group").removeClass("has-success");
                if (d.error)
                    $('.loading').fadeIn('slow').html('<font color="red">Сообщение не отправлено</font>').delay(3000).fadeOut('slow');
                else
                    $('.loading').fadeIn('slow').html('<font color="green">Сообщение успешно отправлено</font>').delay(3000).fadeOut('slow');
                form[0].reset()
            },
            error: function (d) {
                $('.loading').fadeIn('slow').html('<font color="red">Сообщение не отправлено</font>').delay(3000).fadeOut('slow');
            }
        });
        return false;
    });
    $("#reset").click(function () {
        $(".form-group").removeClass("has-success").removeClass("has-error");
    });
})