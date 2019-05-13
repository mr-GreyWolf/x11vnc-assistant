#!/bin/bash

export server_name=`cat /etc/hostname`
export x11vnc_tag=x11vnc-$(whoami)
export flag=/tmp/.x11vnc-$(whoami)
export yad_pid1=/tmp/.x11vnc-$(whoami)-yad-pid1
export yad_pid2=/tmp/.x11vnc-$(whoami)-yad-pid2
export file_passwd=/tmp/.x11vnc-$(whoami)-passwd
export passwd_f=`< /dev/urandom tr -dc 0-9 | head -c${1:-5};echo;`
export passwd_r=`< /dev/urandom tr -dc 0-9 | head -c${1:-3};echo;`

x11vnc_info() {
    if [ -s $yad_pid2 ]; then kill `cat $yad_pid2`; fi
    (
    yad \
        --title="x11vnc" \
        --text "Информация для подключения к сессии:" \
        --window-icon="/usr/local/share/pixmaps/x11vnc.ico" \
	--center \
        --button=gtk-close \
        --form \
	--item-separator="," \
        --field="Имя сервера":RO \
        --field="Номер порта":RO \
        --field="Пароль для управления":RO \
        --field="Пароль для просмотра":RO \
        --field="Список параметров:":TXT \
        "$server_name" "$port" "$passwd_f" "$passwd_r" \
        "$server_name, $port, $passwd_f, $passwd_r" \
    )&
    echo $(echo $!)>$yad_pid2
}

x11vnc_quit() {
    kill `cat $yad_pid1`
    kill `cat $yad_pid2`
    pkill -f $x11vnc_tag
    rm -f $flag
    rm -f $file_passwd
    rm -f $yad_pid1
    rm -f $yad_pid2
}

export -f x11vnc_info
export -f x11vnc_quit

# Выполняем x11vnc_quit
x11vnc_quit

# Сохраняем пароли
echo $passwd_f>$file_passwd
echo "__BEGIN_VIEWONLY__">>$file_passwd
echo $passwd_r>>$file_passwd
chmod u=rw,go= $file_passwd

# Запускаем сервер
x11vnc -q -forever -shared -autoport 5901 -bg -passwdfile $file_passwd -flag $flag -tag $x11vnc_tag -nomodtweak -capslock

if [ -s $flag ] 
    then
	# Получаем номер порта
	export port=`cat $flag |awk -F = '/^PORT=/ {print $2}'`
	# Показ окна с реквизитами
	x11vnc_info 
    else
	# Показ окна с ошибкой
	(
	yad \
	    --title "x11vnc" \
	    --center \
	    --image="gtk-stop" \
	    --window-icon="/usr/local/share/pixmaps/x11vnc.ico" \
	    --text="Запуск x11vnc не выполнен!"\
	    --button=gtk-close \
	)&
	exit
fi
#	    --close-on-unfocus \
# Программа в системной области
(
yad --notification \
    --image="/usr/local/share/pixmaps/x11vnc.ico" \
    --no-middle \
    --text="Подключение к сессии (x11vnc)" \
    --menu='Информация!bash -c "x11vnc_info"!gtk-about|Завершить x11vnc!bash -c "x11vnc_quit"!gtk-quit' \
    --command='bash -c "x11vnc_info %s"' \
)&
echo $(echo $!)>$yad_pid1

exit
