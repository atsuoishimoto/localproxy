localproxy
------------------

HTTP proxy server in twisted. If there is a directory with same name as target host(e.g. www.example.com), contents of the directoy are returned instead of requesting to target host.


Install
=======================

::

    $ git clone https://github.com/atsuoishimoto/localproxy
    $ cd localproxy
    $ python2.7 setup.py install


Usage
======================

The following command invokes localproxy.

::

    $ python2.7 -m localproxy.main


By default, Localproxy wait connection at port 8080. You can change your proxy setting of Web browser to ``localhost:8080``.

To use HTTPS proxy with CONNECT command, you should create your private key and x509 certificate.

::

    $ mkdir ~/my_dir
    $ cd ~/my_dir
    $ openssl genrsa > privkey.pem
    $ openssl req -new -x509 -key privkey.pem -out cacert.pem -days 365


Localproxy reads files from local directory if there is a directory with same name as target host name. Let's say you want to serve files of ``http://www.example.com``, you can create directory and file as follow::

    $ mkdir www.example.com
    $ echo '<html>hello</html>' > www.example.com/index.html

then the file above will be displayed if you open ``http://www.example.com`` with your browser.
