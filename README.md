# qr-code-finder

This is a educational experiment where I developed a kind of QR-code system, with both encoding e decoding functions.

##requirements

opencv with cv2 bindings

numpy

##Usage

to encode the data:
<pre>
  token_encoder.py [data] [width, height] [output file]
</pre>
to find and decode the data: (it will try to use the first camera it finds)
<pre>
  token_locator.py
</pre>
  
