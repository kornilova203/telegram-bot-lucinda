(ql:quickload "hunchentoot")

; create server on 4242 to get requests from telegram
(hunchentoot:start
 (make-instance 'hunchentoot:easy-acceptor :port 4242))

(hunchentoot:define-easy-handler (say-yo :uri "/processwords") (text)
  (setf (hunchentoot:content-type*) "text/plain")
  (format nil "~a!" text)
  (with-open-file (out "~/github/telegram-bot-lucinda/check-post-request.txt"
		       :direction :output
		       :if-exists :append
		       :if-does-not-exist :create)
    (format out "hello, I got this ~a~%" text)))

