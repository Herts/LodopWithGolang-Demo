package main

import (
	"bytes"
	"embed"
	"flag"
	"html/template"
	"io/fs"
	"log"
	"net/http"
	"strings"
	"time"
)

//go:embed static
var assets embed.FS

type Page struct {
	ContractNum string
	TimeNow     string
}

func newHandler(files fs.FS) (http.Handler, error) {
	templates, err := template.ParseFS(files,
		"static/html_templates/print_index.html",
		"static/html_templates/print_main_template.html")
	if err != nil {
		return nil, err
	}
	static, err := fs.Sub(files, "static")
	if err != nil {
		return nil, err
	}
	mux := http.NewServeMux()
	mux.Handle("/static/", http.StripPrefix("/static/", http.FileServer(http.FS(static))))
	mux.HandleFunc("/print/", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet && r.Method != http.MethodHead {
			w.Header().Set("Allow", "GET, HEAD")
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}
		page := Page{
			ContractNum: strings.TrimPrefix(r.URL.Path, "/print/"),
			TimeNow:     time.Now().Format("2006-01-02 15:04"),
		}
		name := "print_main_template.html"
		if page.ContractNum == "" {
			name = "print_index.html"
		}
		var body bytes.Buffer
		if err := templates.ExecuteTemplate(&body, name, page); err != nil {
			log.Printf("render %s: %v", name, err)
			http.Error(w, "Unable to render page", http.StatusInternalServerError)
			return
		}
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		if r.Method != http.MethodHead {
			_, _ = w.Write(body.Bytes())
		}
	})
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/" {
			http.NotFound(w, r)
			return
		}
		http.Redirect(w, r, "/print/", http.StatusFound)
	})
	return mux, nil
}

func main() {
	addr := flag.String("addr", "127.0.0.1:1084", "HTTP listen address")
	flag.Parse()
	handler, err := newHandler(assets)
	if err != nil {
		log.Fatal(err)
	}
	server := &http.Server{
		Addr:              *addr,
		Handler:           handler,
		ReadHeaderTimeout: 5 * time.Second,
		WriteTimeout:      10 * time.Second,
		IdleTimeout:       30 * time.Second,
	}
	log.Printf("Printing demo: http://%s/print/", *addr)
	log.Fatal(server.ListenAndServe())
}
