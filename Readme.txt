PAMIW 2020 - Projekt
KM 1
Nazwa projektu: pamiw2020p1pawelskiba
Adres storny internetowej: https://pamiw2020p1pawelskiba.herokuapp.com/

KM 2
W celu uruchomienia aplikacji należy uruchomić skrypt o nazwie "start_script"
za pomocą polecenia "./start_script",
Skrypt tworzy 2 foldery oraz zmienną środowiskową, którą zapisuje do pliku ".env".
Następnie uruchamiana jest aplikacja. Za pomocą skryptu należy uruchomić aplikację tylko
za pierwszym razem. Następnym razem wystarczy polecenie "sudo docker-compose up".

KM3
Dostępne paczkomaty:
PL079, PL183, PL271

Dostępni kurierzy (login - hasło):
KR023 - Pa$$worD1
KR054 - Pa$$worD2
KR091 - Pa$$worD3

W celu zapiania powyższycz paczkomatów oraz kurierów w bazie danych Redis,
należy wejść na strony główne aplikacji PARCEL_LOCKER_APP oraz COURIER_APP.

Dostępne aplikacje (strony główne):
LOGIN_APP - https://localhost:8080/home/
FILES_APP - https://localhost:8081/home/
PARCEL_LOCKER_APP - https://localhost:8082/user_page/
COURIER_APP - https://localhost:8083/login/

Swagger do każdej aplikacji jest dostępny pod endpointem "/".

W celu uruchomienia projektu należy uruchomić skrypt "start_script",
który jest zamieszcozony w repozytorium.

Aplikację kuriera należy uruchomić z poziomiu linni poleceń (zgodnie z zaleceniem - Bitbucket).
