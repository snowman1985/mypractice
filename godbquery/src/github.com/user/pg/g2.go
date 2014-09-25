package main
import (
	_ "github.com/lib/pq"
	"database/sql"
        "fmt"
)

func main() {
	db, err := sql.Open("postgres", "postgres://postgres:123456@172.18.8.240/csp_active_user?sslmode=disable")

	rows, err := db.Query("SELECT * FROM csp_user_activity_day")
        if err != nil {
          fmt.Print("###have an error")
          fmt.Print(err)         
        }
        fmt.Print(rows)
        columns, err := rows.Columns()
        columncount := len(columns)
        fmt.Println("###column count")
        fmt.Println(columncount)

        for rows.Next() {
        fmt.Println("###new row")
        scanFrom := make([]interface{}, columncount)
        scanTo := make([]interface{}, columncount)
 
        for i, _ := range scanFrom {
        scanFrom[i] = &scanTo[i]
        }


        err1 := rows.Scan(scanFrom...)
        if err1 != nil {
          fmt.Println(err1)
        }
        for _, item := range scanTo {
          fmt.Println(item)
        }
        }
}
