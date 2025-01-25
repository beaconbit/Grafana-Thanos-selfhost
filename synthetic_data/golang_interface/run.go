package main

import (
    "context"
    "fmt"
    "github.com/prometheus/prometheus/model/labels"
    "github.com/prometheus/prometheus/storage"
    "github.com/prometheus/prometheus/tsdb"
    "os"
    "time"
)

func main() {
    // Create a new TSDB instance
    db, err := tsdb.Open(
        "./prometheus-data", // directory where the data will be stored
        nil,      // a logger (can be nil for no logging)
        nil,      // an optional prometheus.Registerer
        tsdb.DefaultOptions(),
        nil,
	)

    if err != nil {
        fmt.Println("Error opening TSDB:", err)
        os.Exit(1)
    }
    defer db.Close()

    // Create a new appender
    app := db.Appender(context.Background())

    // Create labels for the gauge time series
    lbls := labels.FromStrings(
	    "__name__", "fucker", 
	    "type", "gauge",
	    "job", "prometheus",
    )

    // Initialize a SeriesRef
    var ref storage.SeriesRef

    datapoints := 30240

    // Add some data points
    for i := 0; i < datapoints; i++ {
        var err error
	ref, err = app.Append(ref, lbls, (time.Now().Unix() - (14 * 24 * 60 * 60) + int64(i)) * 1000, float64(i))
        if err != nil {
            fmt.Println("Error appending:", err)
            os.Exit(1)
        }
    }

    // Commit the data
    err = app.Commit()
    if err != nil {
        fmt.Println("Error committing:", err)
        os.Exit(1)
    }

    // Compact the TSDB
    if err := db.Compact(context.Background()); err != nil {
    	fmt.Println("error compacting TSDB: ", err)
        os.Exit(1)
    }
}
