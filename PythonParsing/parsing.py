import sys, getopt, glob, os, shutil
import csv, re
import xml.etree.ElementTree as ET


# start parse files
def start_parse(inputdir, outputdir):
    if not os.path.exists(outputdir):
        os.mkdir(outputdir)

    output_file = open(outputdir + "/result.csv", 'w+')
    fieldnames = ['MessageID', 'MessageName', 'WorkNode', 'SenderInformation', 'ReceiverInformation', "File", "Path"]
    writer = csv.DictWriter(output_file, delimiter=";", fieldnames=fieldnames, dialect='excel')
    writer.writeheader()

    for infile in glob.glob(os.path.join(inputdir, '*')):
        if os.path.isdir(infile):
            continue
        with open(infile, 'r', encoding="ISO-8859-1") as f:
            file_str = f.read()
            re1 = re.compile('(.*\s+.*\s.*)<\\?xml.*')
            result = re1.match(file_str)
            if result is not None:
                replace_str = result[1]
                file_without_bytes = file_str.replace(replace_str, "")
                root = ET.fromstring(file_without_bytes)
            else:
                root = ET.parse(infile)
            ns = {
                'ns1': 'urn:customs.ru:Envelope:RoutingInf:1.0',
                'ns2': 'http://www.w3.org/2001/06/soap-envelope',
                'ns3': 'urn:customs.ru:Envelope:Attachments:1.0',
                'ns4': 'urn:customs.ru:Envelope:ApplicationInf:1.0',
            }
            messageId = root.find('.//MessageID', ns)
            messageName = root.find('.//Body/*', ns)
            workNodes = root.findall('.//WorkNode', ns)
            senderInformation = root.find('.//SenderInformation', ns)
            receiverInformation = root.find('.//ReceiverInformation', ns)

            print("%s - %s" % (messageId.tag, messageId.text))
            print("Name - %s" % messageName.tag)
            print("SenderInformation - %s" % senderInformation.text)
            print("ReceiverInformation - %s" % receiverInformation.text)
            workNodesText = ''
            for w in workNodes:
                print("Worknode - %s" % w.text)
                workNodesText += ("%s," % w.text)
            print("-----")
            writer.writerow({
                'MessageID': messageId.text,
                'MessageName': messageName.tag,
                'WorkNode': workNodesText,
                'SenderInformation': senderInformation.text,
                'ReceiverInformation': receiverInformation.text,
                'File': os.path.basename(infile),
                'Path': os.path.abspath(infile),
            })
            f.close()
            shutil.move(infile, outputdir)
    output_file.close()


# main function read arguments
def main(argv):
    try:
        inputdir = ''
        outputdir = ''
        opts, args = getopt.getopt(argv, "hi:o:", ["idir=", "odir="])
        for opt, arg in opts:
            if opt == '-h':
                print('-i <inputdir> -o <outputdir>')
                sys.exit()
            elif opt in ("-i", "--idir"):
                inputdir = arg
            elif opt in ("-o", "--odir"):
                outputdir = arg
        start_parse(inputdir, outputdir)
    except getopt.GetoptError:
        print('-i <inputdir> -o <outputdir>')
    pass


# start here and take arguments
if __name__ == "__main__":
    main(sys.argv[1:])