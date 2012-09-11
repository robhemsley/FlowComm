#include "filedownloader.h"
#include <QDebug>

#include <QFile>

FileDownloader::FileDownloader(QUrl imageUrl, QString fileOutput, QObject *parent) :
    QObject(parent)
{
    connect(&m_WebCtrl, SIGNAL(finished(QNetworkReply*)),
                SLOT(fileDownloaded(QNetworkReply*)));

    QNetworkRequest request(imageUrl);
    m_WebCtrl.get(request);
    fileOutput1 = fileOutput;
}

FileDownloader::~FileDownloader()
{

}

void FileDownloader::fileDownloaded(QNetworkReply* pReply)
{
    m_DownloadedData = pReply->readAll();

    QFile *file = new QFile(fileOutput1);
    if (!file->open(QIODevice::WriteOnly))
        return;

    file->write(m_DownloadedData);
    file->close();
    //emit a signal
    emit downloaded();
}

QByteArray FileDownloader::downloadedData() const
{
    return m_DownloadedData;
}
