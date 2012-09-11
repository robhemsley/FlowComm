#include "copyhandler.h"

#include <QDebug>
#include <QScriptEngine>
#include <QDesktopServices>
#include <QUrl>
#include <QDir>
#include <QFileInfo>

copyHandler::copyHandler(QObject *parent) :
    QObject(parent)
{
}

void copyHandler::process(const QString &param)
{
    qDebug() << "Copy Handler";
    qDebug() << param;
    QScriptValue sc;
    QScriptEngine engine;
    sc = engine.evaluate("(" + QString(param) + ")");
    qDebug() << QString(sc.property("body").toString());

    url = new QUrl(QString(sc.property("body").toString()));
    QFileInfo fileInfo(url->path());
    QString fileName = fileInfo.fileName();
    qDebug() << QDir::homePath()+"/Flow/"+fileName;
    if (QFile::exists(QDir::homePath()+"/Flow/"+fileName)) {
        dataDownloaded();
    }else{
        const FileDownloader * m_pImgCtrl = new FileDownloader(*url, QDir::homePath()+"/Flow/"+fileName, this);
        connect(m_pImgCtrl, SIGNAL(downloaded()), SLOT(dataDownloaded()));
    }
}

void copyHandler::dataDownloaded()
{
    QFileInfo fileInfo(url->path());
    QString fileName = fileInfo.fileName();
    QDesktopServices::openUrl(QUrl::fromLocalFile(QDir::homePath()+"/Flow/"));
}
