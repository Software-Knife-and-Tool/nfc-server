%#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
<p>NDEF Records</p>
<table border="1">
%for row in records:
  <tr>
  %for col in row:
    <td style="padding:10px">{{col}}</td>
  %end
  </tr>
%end
</table>
