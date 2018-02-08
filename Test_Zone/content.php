<?php
echo "<h1>Отзывы</h1><br/>";
?>
<?php
if (isset($_REQUEST['ok'])) {
 
    $string = '<div class="comment"><div class="alert alert-info" role="alert">
	<b><xmp>Имя : '.$_REQUEST['username'].'</xmp></b><div class="alert alert-warning" role="alert">
	<xmp>Текст : '.$_REQUEST['msg'].'</xmp></div></div></div>';
    file_put_contents('comm.bd', $string, FILE_APPEND);
}
include ('comm.bd');
?>
<div class="row">
<form>
<h1>Оставить отзыв</h1>
  <div class="form-group">
    <label for="exampleInputEmail1">Имя пользователя</label>
    <input type="text" class="form-control" id="exampleInputEmail1" name="username" aria-describedby="emailHelp" placeholder="Введите имя">
    <small id="emailHelp" class="form-text text-muted">Тут подсказка</small>
  </div>
  <div class="form-group">
    <label for="exampleFormControlTextarea1">Текст сообщения</label>
    <textarea name="msg" class="form-control" id="exampleFormControlTextarea1" rows="3"></textarea>
  </div>
  <!--div class="form-check">
    <input type="checkbox" class="form-check-input" id="exampleCheck1">
    <label class="form-check-label" for="exampleCheck1">Check me out</label>
  </div-->
  <button type="submit" name="ok" class="btn btn-primary">Submit</button>
</form>
</div>