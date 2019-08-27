package main

import (
	"html/template"
	"log"
	"net/http"
	"time"
)

type Page struct {
	ContractNum      string
	ContractVer      string
	ContractType     string
	ContractTypeCN   string
	ContractBranch   string
	ContractBranchCN string
	UrlParameters    string
	TimeNow          string
	NumOfAccess      int
	PageOffsetConfig template.HTML
}

func printHandler(w http.ResponseWriter, r *http.Request) {
	log.Println("printHandler -> request received from", r.URL.Path)

	path := r.URL.Path
	path = path[len("/print/"):]
	log.Println("printHandler -> path:", path)
	if len(path) == 0 {
		t, err := template.ParseFiles("./static/html_templates/print_index.html")
		if err != nil {
			log.Println("printHandler ->", err)
		}
		p := &Page{
			TimeNow: time.Now().Format("2006-01-02 15:04"),
		}
		t.Execute(w, p)
		return
	}

	const TEMPLATE_URL string = "./static/html_templates/print_main_template.html"
	t, err := template.ParseFiles(TEMPLATE_URL)
	if err != nil {
		log.Println("printHandler ->", err)
	}

	p := &Page{
		ContractNum: path,
	}
	t.Execute(w, p)

	log.Println("printHandler -> response created")
	// Debug the output:
	//var buf bytes.Buffer
	//t.Execute(&buf, p)
	//log.Println("printHandler -> response created:", buf.String())
}

func main() {
	http.HandleFunc("/print/", printHandler)
	http.Handle("/static/", http.StripPrefix("/static/", http.FileServer(http.Dir("static"))))
	log.Fatal(http.ListenAndServe(":1084", nil))

}
