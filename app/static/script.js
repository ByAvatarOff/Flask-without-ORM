//$(document).ready(function() {
//     $('form').on('submit', function(event) {
//       $.ajax({
//          data : {
//             fio : form.fio.data,
//             position_id: form.position_id.data,
//             department_id: form.department_id.data,
//                 },
//             type : 'POST',
//             url : '/employee/add'
//            })
//        .done(function(data) {
//          $('#output').text(data.output).show();
//      });
//      event.preventDefault();
//      });
//});