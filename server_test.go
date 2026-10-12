package main

import (
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"testing/fstest"
)

func TestRoutes(t *testing.T) {
	handler, err := newHandler(assets)
	if err != nil {
		t.Fatal(err)
	}
	for _, tc := range []struct {
		method, path string
		status       int
		contains     string
	}{
		{"GET", "/", 302, "/print/"},
		{"GET", "/print/", 200, "Contract printing demo"},
		{"GET", "/print/123", 200, "123"},
		{"GET", "/print/%3Cscript%3E", 200, "&lt;script&gt;"},
		{"GET", "/static/json/demo.json", 200, `"contractNum"`},
		{"GET", "/static/js/demo.js", 200, "CreatePrintPage"},
		{"GET", "/missing", 404, "404"},
		{"GET", "/static/missing", 404, "404"},
		{"POST", "/print/123", 405, "Method not allowed"},
		{"HEAD", "/print/123", 200, ""},
	} {
		t.Run(tc.method+tc.path, func(t *testing.T) {
			response := httptest.NewRecorder()
			handler.ServeHTTP(response, httptest.NewRequest(tc.method, tc.path, nil))
			if response.Code != tc.status || !strings.Contains(response.Body.String(), tc.contains) {
				t.Fatalf("got %d %q", response.Code, response.Body.String())
			}
			if tc.method == "HEAD" && response.Body.Len() != 0 {
				t.Fatal("HEAD returned a response body")
			}
		})
	}
}

func TestMissingOrInvalidTemplates(t *testing.T) {
	for _, files := range []fstest.MapFS{
		{},
		{"static/html_templates/print_index.html": {Data: []byte("{{")},
			"static/html_templates/print_main_template.html": {Data: []byte("demo")}},
	} {
		if _, err := newHandler(files); err == nil {
			t.Fatal("invalid templates must fail at startup")
		}
	}
}

func TestRenderFailureDoesNotWritePartialHTML(t *testing.T) {
	files := fstest.MapFS{
		"static/html_templates/print_index.html":         {Data: []byte("index")},
		"static/html_templates/print_main_template.html": {Data: []byte("partial {{.MissingField}}")},
	}
	handler, err := newHandler(files)
	if err != nil {
		t.Fatal(err)
	}
	response := httptest.NewRecorder()
	handler.ServeHTTP(response, httptest.NewRequest(http.MethodGet, "/print/123", nil))
	if response.Code != 500 || strings.Contains(response.Body.String(), "partial") {
		t.Fatalf("got %d %q", response.Code, response.Body.String())
	}
}
