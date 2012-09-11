#include "openhandler.h"
#include <QDebug>
#include <QScriptEngine>
#include <QDesktopServices>
#include <QUrl>

openHandler::openHandler(QObject *parent) :
    QObject(parent)
{
}

void openHandler::process(const QString &param)
{
    qDebug() << "Open Handler";
    qDebug() << param;
    QScriptValue sc;
    QScriptEngine engine;
    sc = engine.evaluate("(" + QString(param) + ")");
    qDebug() << QString(sc.property("body").toString());

    QDesktopServices::openUrl(QUrl(QString(sc.property("body").toString()), QUrl::TolerantMode));
}
