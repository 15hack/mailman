cp _admins.txt admins.txt
if [ -f "$1" ]; then
    cat "$1" >>  admins.txt
fi
./owners.sh >> admins.txt
sort -f admins.txt | uniq -i > a.txt
./members.sh > members.txt
sort -f members.txt | uniq -i > b.txt
# Nos quedamos con los administradores que no son miembros de ninguna lista
comm a.txt b.txt -23
