#ifndef OPENHANDLER_H
#define OPENHANDLER_H

#include <QObject>

class openHandler : public QObject
{
    Q_OBJECT
public:
    explicit openHandler(QObject *parent = 0);
    
signals:
    
public slots:
    void process(const QString &param);
};

#endif // OPENHANDLER_H
