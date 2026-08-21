#include "tinyxml2.h"
#include <iostream>
#include <vector>

using namespace tinyxml2;

void traverse_nodes(const XMLNode* node, int depth) {
    if (!node || depth > 30) return;
    for (const XMLNode* child = node->FirstChild(); child; child = child->NextSibling()) {
        const XMLElement* element = child->ToElement();
        if (element) {
            const XMLAttribute* attr = element->FirstAttribute();
            while (attr) {
                attr->Name();
                attr->Value();
                attr = attr->Next();
            }
        }
        traverse_nodes(child, depth + 1);
    }
}

int main(int argc, char** argv) {
    if (argc < 2) return 1;

    XMLDocument doc;
    XMLError err = doc.LoadFile(argv[1]);
    if (err == XML_SUCCESS) {
        traverse_nodes(&doc, 0);
        XMLPrinter printer;
        doc.Print(&printer);
    }
    return 0;
}
