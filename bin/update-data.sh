#!/bin/sh

# The VegaDNS2 tinydns export endpoint
# Can be a space delimited list of VegaDNS2 servers
VEGADNS='http://127.0.0.1/1.0/export/tinydns'

# Path to the tinydns directory
TINYDNSDIR=/etc/tinydns

CUR="$TINYDNSDIR/root/data"
OLD="$TINYDNSDIR/root/data.old"
NEW="$TINYDNSDIR/root/data.new"


if [ -f "$CUR" ] ; then
    cp $CUR $OLD
fi

if [ -f "$NEW" ] ; then
    rm $NEW
fi

A=$[0]
for VD in $VEGADNS ; do
    A=$[$A+1]
    if wget -q -O "$TINYDNSDIR/root/data.srv-$A" $VD ; then
        if [ -s "$TINYDNSDIR/root/data.srv-$A" ] ; then
            cat "$TINYDNSDIR/root/data.srv-$A" >>$NEW
        else
            echo "ERROR: $TINYDNSDIR/root/data.srv-$A does not have a size greater than zero" 1>&2
            exit 1
        fi
    else
        echo "ERROR: wget did not return 0 when accessing $VD" 1>&2
        exit 1
    fi
    if [ -f "$TINYDNSDIR/root/data.srv-$A" ] ; then
        rm "$TINYDNSDIR/root/data.srv-$A"
    fi
done

# Don't run make if the files havn't changed
OLDSUM=$(sum $OLD | awk '{ print $1 " " $2}')
NEWSUM=$(sum $NEW | awk '{ print $1 " " $2}')

if [ "$OLDSUM" != "$NEWSUM" ]; then
    mv $NEW $CUR
    (cd $TINYDNSDIR/root ; make -s)
else
    rm $NEW
fi

diff -u $OLD $CUR
exit 0
