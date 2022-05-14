(function status(){
  $('#password').keyup(function(){
  if($('#password').val().length>=8){
    $('font[name=check1]').text('');
    $('font[name=check1]').html("");
  }
  else{
    $('font[name=check1]').text('');
    $('font[name=check1]').html("암호다시입력");
  }


  }); //#user_pass.keyup

  $('#passwordagain').keyup(function(){
   if($('#password').val()!=$('#passwordagain').val()){
    $('font[name=check]').text('');
    $('font[name=check]').html("암호틀림");
   }else{
    $('font[name=check]').text('');
    $('font[name=check]').html("");
   }
  }); //#chpass.keyup
 })();